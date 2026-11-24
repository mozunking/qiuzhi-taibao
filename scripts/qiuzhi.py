#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""求职台 · 统一命令行（qiuzhi）

面向计算机类岗位的应届生求职：筛岗 → 评分 → 投递计划 → 台账 → 面试 → 复盘。
纯标准库、零依赖、不联网；数据只落本地 JSON。

先看功能：
    python3 qiuzhi.py help

典型流程：
    python3 qiuzhi.py init --name 张三 --major 物联网工程 --degree 本科 --grad 2027 \
        --cities 石家庄,成都 --skills Java,MySQL,Linux,Python --projects 2
    python3 qiuzhi.py add-job --co 国网河北省电力 --role 电子信息类 --city 石家庄 \
        --due 2026-11-25 --major-list "计算机科学与技术,软件工程,人工智能" \
        --bachelor-ok --headcount 65
    python3 qiuzhi.py check-major --major 物联网工程 --major-list "计算机科学与技术,软件工程"
    python3 qiuzhi.py score
    python3 qiuzhi.py plan
    python3 qiuzhi.py tracker --out 求职台账.html
    python3 qiuzhi.py interview --n 8 --level L2
"""
import argparse
import json
import os
import sys
import datetime
import random

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(HERE)
DEFAULT_DATA = os.path.join(SKILL_ROOT, "data")

# ---------------------------------------------------------------- 岗位族系数
# 成长性：同一份力气，五年后能带走多少。（借鉴"岗位职能"这一维）
ROLE_FAMILY = {
    "算法": 1.00, "后端": 0.95, "服务端": 0.95, "数据": 0.90,
    "前端": 0.80, "客户端": 0.80, "全栈": 0.85, "安全": 0.85,
    "嵌入式": 0.80, "测试": 0.65, "测开": 0.75, "运维": 0.60,
    "sre": 0.65, "实施": 0.45, "解决方案": 0.50, "产品": 0.75,
    "技术支持": 0.45, "运维开发": 0.70,
}
# 各岗位族常见技术栈（job 没填 stack 时用作默认比对集）
FAMILY_STACK = {
    "后端": ["Java", "Spring", "MySQL", "Redis", "Linux", "MQ", "微服务"],
    "前端": ["JavaScript", "TypeScript", "Vue", "React", "CSS", "HTML"],
    "客户端": ["Java", "Kotlin", "Swift", "C++", "Android", "iOS"],
    "算法": ["Python", "C++", "PyTorch", "TensorFlow", "机器学习", "深度学习"],
    "数据": ["SQL", "Python", "Hive", "Spark", "Flink", "数据仓库"],
    "测试": ["Python", "自动化测试", "Selenium", "接口测试", "Linux"],
    "运维": ["Linux", "Shell", "Docker", "K8s", "网络", "监控"],
    "嵌入式": ["C", "C++", "单片机", "RTOS", "Linux", "驱动"],
    "安全": ["渗透测试", "漏洞", "密码学", "网络", "Linux"],
}

LEVEL_ORDER = {"不可投": 0, "过期": 1, "不建议": 2, "保": 3, "稳": 4, "冲": 5}

# ---------------------------------------------------------------- 题库（内置精简版）
BANK = [
    ("L0", "进程和线程的区别？", "考察地址空间、调度单位、通信与开销"),
    ("L0", "TCP 三次握手为什么不是两次？", "考察历史连接、序列号同步、资源分配"),
    ("L0", "HTTP 和 HTTPS 的区别？", "考察加密层、证书、性能代价"),
    ("L0", "数组和链表的区别与适用场景？", "考察随机访问、插入删除、缓存友好"),
    ("L0", "什么是死锁？四个必要条件？", "考察互斥、占有等待、不可剥夺、循环等待"),
    ("L0", "数据库索引为什么能加速查询？", "考察 B+ 树、顺序 IO、回表"),
    ("L1", "MySQL 索引为什么用 B+ 树而不是红黑树？", "考察树高、磁盘 IO、范围查询"),
    ("L1", "Redis 为什么快？单线程为什么还能高并发？", "考察内存、IO 多路复用、数据结构"),
    ("L1", "垃圾回收的分代假设是什么？", "考察对象存活率、晋升、STW"),
    ("L1", "Spring Bean 的生命周期？", "考察实例化、初始化、AOP 代理、销毁"),
    ("L1", "K8s 的 Pod 和容器是什么关系？", "考察共享网络/存储、调度单位"),
    ("L1", "HTTP/2 相比 HTTP/1.1 改了什么？", "考察多路复用、头部压缩、队头阻塞"),
    ("L2", "线上接口 P99 从 100ms 涨到 2s，你怎么查？", "考察监控—链路—日志—复现—定位的顺序"),
    ("L2", "缓存雪崩、击穿、穿透怎么分别防？", "考察随机过期、互斥重建、布隆过滤"),
    ("L2", "消息队列丢消息可能发生在哪几个环节？", "考察生产、broker、消费、幂等"),
    ("L2", "慢 SQL 怎么定位与优化？", "考察执行计划、索引、回表、分页"),
    ("L2", "分布式事务有哪些方案？各有什么代价？", "考察 2PC、TCC、Saga、本地消息表"),
    ("L2", "接口幂等怎么实现？", "考察 token、唯一键、状态机"),
    ("L3", "设计一个短链服务，要支撑 1 亿条。", "考察发号、映射、缓存、跳转、统计"),
    ("L3", "设计一个秒杀系统，重点防什么？", "考察削峰、限流、库存扣减、超卖"),
    ("L3", "为什么选消息队列而不是同步调用？", "考察解耦、削峰、最终一致、复杂度"),
    ("L3", "设计一个日志采集系统，日增 10TB。", "考察采集、传输、存储、索引、成本"),
    ("L3", "一个接口要做多级缓存，怎么保证一致性？", "考察失效策略、延迟双删、版本号"),
    ("L3", "设计一个分布式 ID 生成器。", "考察雪花、号段、时钟回拨"),
    ("L4", "你负责的模块要迁到云上，怎么保证不丢数据？", "考察双写、校验、灰度、回滚"),
    ("L4", "团队技术债很重，你怎么排优先级？", "考察量化影响、成本收益、沟通"),
    ("L4", "线上出故障你先做什么？", "考察止损优先、信息同步、复盘"),
    ("L4", "你怎么衡量自己这半年有没有成长？", "考察指标、反馈、可迁移能力"),
    ("L4", "让你带一个新人，你怎么安排前三个月？", "考察目标拆解、反馈节奏"),
    ("L4", "为什么选我们这家公司这个岗位？", "考察动机真实性与匹配度"),
]


# ---------------------------------------------------------------- 工具
def today():
    return datetime.date.today()


def parse_date(s):
    if not s:
        return None
    try:
        return datetime.date.fromisoformat(s)
    except Exception:
        return None


def days_left(due):
    d = parse_date(due)
    if not d:
        return None
    return (d - today()).days


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def paths(data_dir):
    return (os.path.join(data_dir, "profile.json"),
            os.path.join(data_dir, "jobs.json"))


def load_state(data_dir):
    p, j = paths(data_dir)
    return load_json(p, {}), load_json(j, [])


# ---------------------------------------------------------------- 专业口径判定
WIDE_MARKERS = ["等", "及相关", "相关专业", "以.*类为主", "类为主", "相近专业", "及其相关"]


def judge_major(major, major_list, notice_text=""):
    """返回 (风险等级, 理由, 建议动作)。等级：低/中/高"""
    names = [x.strip() for x in (major_list or "").replace("、", ",").replace("，", ",").split(",") if x.strip()]
    blob = " ".join(names) + " " + (notice_text or "")
    m = (major or "").strip()

    if m and any(m == n for n in names):
        return ("低", f"公告名单已点名列明「{m}」", "可直接投，报名时按公告上传材料即可")
    if m and any(m in n or n in m for n in names if n):
        hit = next(n for n in names if m in n or n in m)
        return ("低", f"名单中的「{hit}」与你的专业高度接近", "可直接投；面试前备好一句专业方向的解释")
    wide = [w for w in ["等", "及相关", "相关专业", "类为主", "相近专业", "及其相关"] if w in blob]
    if wide:
        return ("中", f"名单未点名，但公告用了宽松表述（{'/'.join(wide)}）",
                "可投；建议报名前打公告电话确认一句，留好通话记录")
    return ("高", "名单是封闭列举且未点名你的专业，公告无宽松表述",
            "必须先电话确认再投：'我是XX专业，公告电子信息类下列的是XX等专业，请问我的专业按该类受理吗？'")


# ---------------------------------------------------------------- 评分
def score_job(profile, job):
    """返回 dict：score / level / dims / reasons / risks"""
    dims, reasons, risks = {}, [], []
    skills = [s.strip().lower() for s in profile.get("skills", []) if s.strip()]
    cities = [c.strip() for c in profile.get("cities", []) if c.strip()]
    projects = int(profile.get("projects", 0) or 0)

    # --- 硬门槛
    hard_block = False
    deg_rank = {"专科": 1, "本科": 2, "硕士": 3, "博士": 4}
    my_deg = deg_rank.get(profile.get("degree", "本科"), 2)
    need_deg = deg_rank.get(job.get("degree_min", "本科"), 2)
    if need_deg > my_deg:
        hard_block = True
        risks.append(f"学历门槛 {job.get('degree_min')} 高于你的 {profile.get('degree')}")
    if job.get("bachelor_ok") is False:
        hard_block = True
        risks.append("该岗位明确不招本科")

    risk, why, action = judge_major(profile.get("major", ""),
                                    job.get("major_list", ""),
                                    job.get("notice_text", ""))
    if risk == "高":
        risks.append("专业口径高风险：" + why)

    dl = days_left(job.get("due", ""))
    expired = dl is not None and dl < 0
    if expired:
        risks.append(f"报名已截止（{job.get('due')}，逾期 {-dl} 天）")

    # --- 技术栈匹配 30
    fam = (job.get("family") or "").lower()
    stack = [x.strip().lower() for x in (job.get("stack") or "").replace("、", ",").split(",") if x.strip()]
    if not stack:
        for k, v in FAMILY_STACK.items():
            if k in fam or k in (job.get("role", "") or ""):
                stack = [x.lower() for x in v]
                break
    if stack and skills:
        hit = [s for s in stack if any(sk in s or s in sk for sk in skills)]
        tech = len(hit) / float(len(stack))
    else:
        tech = 0.4 if skills else 0.2
    dims["技术栈匹配"] = round(30 * tech, 1)
    if stack:
        miss = [s for s in stack if s not in hit]
        if miss:
            reasons.append("技能缺口：" + "、".join(miss[:5]))

    # --- 经历证据 20
    ev = min(1.0, projects * 0.3 + (0.2 if profile.get("intern") else 0) + (0.15 if profile.get("certs") else 0))
    dims["经历证据"] = round(20 * ev, 1)
    if projects == 0 and not profile.get("intern"):
        risks.append("没有项目和实习，面试第一轮就容易被问空")

    # --- 岗位成长性 20
    grow = 0.6
    for k, v in ROLE_FAMILY.items():
        if k in fam or k in (job.get("role", "") or ""):
            grow = v
            break
    dims["成长性"] = round(20 * grow, 1)

    # --- 上岸概率 20
    chance = 0.0
    if job.get("bachelor_ok"):
        chance += 0.4
    hc = job.get("headcount")
    if isinstance(hc, (int, float)) and hc > 0:
        chance += 0.4 * min(1.0, hc / 200.0)
    else:
        chance += 0.15
    chance += 0.2 * {"低": 1.0, "中": 0.6, "高": 0.2}.get(risk, 0.4)
    dims["上岸概率"] = round(20 * min(1.0, chance), 1)

    # --- 地理与生活 10
    city = job.get("city", "") or ""
    if cities and any(c in city for c in cities):
        geo = 1.0
    elif profile.get("home_province") and profile.get("home_province") in city:
        geo = 0.7
    elif job.get("remote"):
        geo = 0.8
    else:
        geo = 0.45
        if cities:
            reasons.append(f"城市不在偏好（你在{'/'.join(cities)}）")
    dims["地理与生活"] = round(10 * geo, 1)

    total = sum(dims.values())
    if risk == "高":
        total -= 15
        reasons.append("专业口径未确认，扣 15 分")
    if cities and geo < 0.5:
        total -= 5
        reasons.append("异地，扣 5 分")

    total = max(0.0, min(100.0, round(total, 1)))

    if hard_block:
        level = "不可投"
    elif expired:
        level = "过期"
    elif total >= 80:
        level = "冲"
    elif total >= 65:
        level = "稳"
    elif total >= 50:
        level = "保"
    else:
        level = "不建议"

    return {"score": total, "level": level, "dims": dims,
            "reasons": reasons, "risks": risks,
            "major_risk": risk, "major_action": action, "days_left": dl}


# ---------------------------------------------------------------- 子命令
def cmd_help(args):
    _ver = "3.1.0"
    _vp = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "VERSION")
    if os.path.exists(_vp):
        try: _ver = open(_vp, encoding="utf-8").read().strip()
        except Exception: pass
    print(f"""求职台 v{_ver} · 命令总览
=====================
这是给"计算机类岗位应届生"用的本地工具箱，全部离线运行。

1) 写画像（只需一次）
   python3 qiuzhi.py init --name 张三 --major 物联网工程 --degree 本科 --grad 2027 \\
       --cities 石家庄,成都 --skills Java,MySQL,Linux,Python --projects 2 --intern
   参数：--certs（有计算机等级证）、--home-province 河北、--allow-remote

2) 录岗位（一条一条，或写脚本批量调）
   python3 qiuzhi.py add-job --co 国网河北省电力 --role 电子信息类 --city 石家庄 \\
       --due 2026-11-25 --major-list "计算机科学与技术,软件工程" --bachelor-ok --headcount 65 \\
       --family 后端 --stack "Java,MySQL,Linux" --url zhaopin.sgcc.com.cn
   关键参数：--major-list 公告专业名单原文；--notice-text 公告里的专业描述段；--bachelor-ok/--no-bachelor

3) 专业口径判风险（最该先跑的一步）
   python3 qiuzhi.py check-major --major 物联网工程 \\
       --major-list "计算机科学与技术,软件工程,人工智能" \\
       --notice-text "招聘专业以电工类和电子信息类为主"
   输出：低/中/高 风险 + 直接能念的电话话术

4) 打分（五维：技术栈30 / 经历20 / 成长性20 / 上岸20 / 地理10）
   python3 qiuzhi.py score             # 全部岗位
   python3 qiuzhi.py score --id 3      # 单个岗位

5) 投递计划（冲/稳/保 + 截止排序 + 笔试撞车提示）
   python3 qiuzhi.py plan

6) 台账（生成单文件 HTML，双击浏览器打开，可导出 JSON）
   python3 qiuzhi.py tracker --out 求职台账.html

7) 面试（按级别抽题 + 三层追问 + 打分表）
   python3 qiuzhi.py interview --n 8 --level L2

8) 复盘模板
   python3 qiuzhi.py review

9) 查看已录岗位
   python3 qiuzhi.py list

数据位置：技能目录下 data/profile.json 与 data/jobs.json（换 --data-dir 可换一套）。
不联网、不上传；换电脑前把 data 目录一起拷走。""")


def cmd_init(args):
    p_path, _ = paths(args.data_dir)
    profile = {
        "name": args.name,
        "major": args.major,
        "degree": args.degree,
        "grad_year": args.grad,
        "cities": [x.strip() for x in (args.cities or "").split(",") if x.strip()],
        "skills": [x.strip() for x in (args.skills or "").split(",") if x.strip()],
        "projects": args.projects,
        "intern": args.intern,
        "certs": args.certs,
        "home_province": args.home_province or "",
        "allow_remote": args.allow_remote,
    }
    save_json(p_path, profile)
    print(f"画像已保存：{p_path}")
    print(json.dumps(profile, ensure_ascii=False, indent=2))
    risk, why, action = judge_major(profile["major"], "", "")
    print(f"\n提示：你的专业「{profile['major']}」还没对照任何公告。录岗位时务必带 --major-list。")


def cmd_add_job(args):
    _, j_path = paths(args.data_dir)
    jobs = load_json(j_path, [])
    job = {
        "id": max([j.get("id", 0) for j in jobs] + [0]) + 1,
        "co": args.co, "role": args.role or "", "city": args.city or "",
        "due": args.due or "", "major_list": args.major_list or "",
        "notice_text": args.notice_text or "", "headcount": args.headcount,
        "bachelor_ok": (True if args.bachelor_ok else (False if args.no_bachelor else None)),
        "degree_min": args.degree_min, "family": args.family or "",
        "stack": args.stack or "", "url": args.url or "", "note": args.note or "",
        "remote": args.remote, "status": "待投",
    }
    jobs.append(job)
    save_json(j_path, jobs)
    print(f"已加入 #{job['id']} {job['co']} / {job['role']}（共 {len(jobs)} 条）")


def cmd_list(args):
    _, j_path = paths(args.data_dir)
    jobs = load_json(j_path, [])
    if not jobs:
        print("还没有岗位。用 add-job 加一条，或先跑 help 看示例。")
        return
    print(f"{'ID':<3} {'单位':<22} {'岗位':<16} {'城市':<10} {'截止':<11} 状态")
    for j in jobs:
        print(f"{j.get('id',''):<3} {j.get('co','')[:20]:<22} {j.get('role','')[:14]:<16} "
              f"{j.get('city','')[:8]:<10} {j.get('due',''):<11} {j.get('status','')}")


def cmd_check_major(args):
    risk, why, action = judge_major(args.major, args.major_list, args.notice_text)
    print(f"专业：{args.major}")
    print(f"风险：{risk}")
    print(f"理由：{why}")
    print(f"动作：{action}")
    if risk == "高":
        print("\n可以照着念的话术：")
        print(f"  '老师您好，我是XX大学 {args.major} 专业 2027 届本科毕业生。看到公告里这个岗位的专业列的是"
              f"{args.major_list or '若干专业'}，我的专业是{args.major}，请问按哪一类受理？需要额外上传材料吗？'")
    sys.exit(0 if risk != "高" else 2)


def cmd_score(args):
    profile, _ = load_state(args.data_dir)
    _, j_path = paths(args.data_dir)
    jobs = load_json(j_path, [])
    if not profile:
        print("先跑 init 建画像。")
        return
    if not jobs:
        print("还没有岗位，先 add-job。")
        return
    results = []
    for j in jobs:
        r = score_job(profile, j)
        j["_score"] = r
        results.append((j, r))
    save_json(j_path, jobs)

    targets = results if not args.id else [x for x in results if x[0].get("id") == args.id]
    for j, r in targets:
        dl = r["days_left"]
        dltxt = "—" if dl is None else ("已过 %d 天" % -dl if dl < 0 else "剩 %d 天" % dl)
        print("=" * 66)
        print(f"#{j['id']} {j['co']} / {j['role']}  [{j.get('city','')}]")
        print(f"  总分 {r['score']}  分级 {r['level']}  专业风险 {r['major_risk']}  截止 {j.get('due') or '—'}（{dltxt}）")
        print("  维度： " + "  ".join(f"{k} {v}" for k, v in r["dims"].items()))
        for x in r["reasons"]:
            print("  · 扣分/缺口：" + x)
        for x in r["risks"]:
            print("  ! 风险：" + x)
        print("  → 专业口径动作：" + r["major_action"])
    print("=" * 66)
    print("提示：低于 50 分或专业高风险的不必硬投；先跑 plan 看投递顺序。")


def cmd_plan(args):
    profile, _ = load_state(args.data_dir)
    _, j_path = paths(args.data_dir)
    jobs = load_json(j_path, [])
    if not jobs:
        print("还没有岗位，先 add-job。")
        return
    rows = []
    for j in jobs:
        r = j.get("_score") or score_job(profile, j)
        rows.append((j, r))

    buckets = {"冲": [], "稳": [], "保": [], "不建议": [], "不可投": [], "过期": []}
    for j, r in rows:
        buckets.setdefault(r["level"], []).append((j, r))
    for k in buckets:
        buckets[k].sort(key=lambda x: (x[1]["days_left"] if x[1]["days_left"] is not None else 9999))

    print("投递计划（按截止时间排，越靠前越急）")
    print(f"画像：{profile.get('major','?')} / {profile.get('degree','?')} / 偏好城市 {'/'.join(profile.get('cities',[])) or '不限'}")
    for level in ["冲", "稳", "保", "不建议", "不可投", "过期"]:
        arr = buckets.get(level, [])
        if not arr:
            continue
        print(f"\n【{level}】{len(arr)} 条")
        for j, r in arr:
            dl = r["days_left"]
            dltxt = "—" if dl is None else (f"逾期{-dl}天" if dl < 0 else f"剩{dl}天")
            flag = " ★专业待确认" if r["major_risk"] == "高" else ""
            print(f"  #{j['id']:<3} {r['score']:>5}  {j['co'][:18]:<20} {j.get('role','')[:12]:<14} "
                  f"{j.get('city','')[:8]:<10} {j.get('due','') or '—':<11}{dltxt}{flag}")

    # 时间冲突
    bydate = {}
    for j, r in rows:
        d = j.get("due")
        if d and r["level"] in ("冲", "稳", "保"):
            bydate.setdefault(d, []).append(j["co"])
    conflicts = {d: v for d, v in bydate.items() if len(v) > 1}
    if conflicts:
        print("\n! 笔试/面试时间密集提醒（同一截止日的可能撞车，笔试通常只能选一家考）：")
        for d, v in sorted(conflicts.items()):
            print(f"  {d}：{'、'.join(v)}")

    # 建议配比
    n = {k: len(v) for k, v in buckets.items()}
    print(f"\n配比自检：冲 {n.get('冲',0)} / 稳 {n.get('稳',0)} / 保 {n.get('保',0)}")
    if n.get("保", 0) == 0:
        print("  → 你还没有「保底」档，建议至少加 1-2 个录取概率高的（地方国企、中小厂、县公司）。")
    if n.get("冲", 0) > 3:
        print("  → 冲刺档超过 3 个，精力会摊薄，建议只留最想去的 2-3 个。")
    high_risk = [j["co"] for j, r in rows
                 if r["major_risk"] == "高" and r["level"] not in ("过期", "不可投")]
    if high_risk:
        print(f"\n建议动作：先打这几家的专业确认电话 → {'、'.join(high_risk)}；确认能报再投，别先花时间改简历。")
    else:
        print("\n建议动作：专业口径都无高风险，按截止日顺序投即可；先投截止最近的。")


def cmd_tracker(args):
    import subprocess
    _, j_path = paths(args.data_dir)
    jobs = load_json(j_path, [])
    seed = []
    for j in jobs:
        r = j.get("_score") or {}
        note = j.get("note", "")
        if r:
            note = (note + f" | 评分{r.get('score')}·{r.get('level')}·专业风险{r.get('major_risk')}").strip(" |")
        seed.append({
            "co": j.get("co", ""), "role": j.get("role", ""), "city": j.get("city", ""),
            "major": j.get("major_list", "")[:80], "url": j.get("url", ""),
            "due": j.get("due", ""), "status": j.get("status", "待投"),
            "resume": "", "note": note,
        })
    seed_path = os.path.join(args.data_dir, "_seed.json")
    save_json(seed_path, seed)
    out = args.out or "求职台账.html"
    cmd = [sys.executable, os.path.join(HERE, "make_tracker.py"), "--out", out, "--seed", seed_path]
    if args.name:
        cmd += ["--name", args.name]
    rc = subprocess.call(cmd)
    if rc == 0:
        print(f"台账已生成：{os.path.abspath(out)}（含 {len(seed)} 条岗位与评分）")


def cmd_interview(args):
    levels = [args.level.upper()] if args.level else ["L0", "L1", "L2", "L3", "L4"]
    pool = [q for q in BANK if q[0] in levels]
    n = min(args.n, len(pool))
    picked = random.sample(pool, n) if args.shuffle else pool[:n]
    picked.sort(key=lambda x: x[0])
    print(f"模拟面试：{n} 题（{'/'.join(levels)}）")
    print("规则：每题先自己说 60-90 秒，再接受三层追问（机制细节 → 边界权衡 → 实战度量）。")
    print("-" * 66)
    for i, (lv, q, focus) in enumerate(picked, 1):
        print(f"{i:>2}. [{lv}] {q}")
        print(f"    考察：{focus}")
    print("-" * 66)
    print("""打分（合计 100）：
  证据覆盖 40 | 正确性 20 | 个人边界 15 | 指标与口径 15 | 表达结构 10
  证据状态：已验证 / 部分验证 / 未验证(≤70) / 矛盾(≤50) / 未覆盖
参考答法目标分 80：说全了但留有余地。答不上来说'没做过，我的理解是…'，不要编。""")
    if args.answer:
        print("\n参考答法要点：")
        for lv, q, focus in picked:
            print(f"  [{lv}] {q} → {focus}")


def cmd_review(args):
    p = os.path.join(SKILL_ROOT, "assets", "复盘表模板.md")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            print(f.read())
    else:
        print("复盘模板缺失，请检查 assets/复盘表模板.md")


# ---------------------------------------------------------------- main
def build_parser():
    ap = argparse.ArgumentParser(prog="qiuzhi", description="求职台：筛岗→评分→投递计划→台账→面试→复盘")
    ap.add_argument("--data-dir", default=DEFAULT_DATA, help="数据目录（默认技能目录下 data/）")
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("help", help="功能总览与调用示例")

    p = sub.add_parser("init", help="建立个人画像")
    p.add_argument("--name", default="我")
    p.add_argument("--major", required=True, help="学信网专业全名，如 物联网工程")
    p.add_argument("--degree", default="本科", choices=["专科", "本科", "硕士", "博士"])
    p.add_argument("--grad", default="", help="毕业年份，如 2027")
    p.add_argument("--cities", default="", help="偏好城市，逗号分隔")
    p.add_argument("--skills", default="", help="技能，逗号分隔")
    p.add_argument("--projects", type=int, default=0, help="可写进简历的项目数")
    p.add_argument("--intern", action="store_true", help="有实习经历")
    p.add_argument("--certs", action="store_true", help="有计算机等级/职业证书")
    p.add_argument("--home-province", default="", help="家乡省份，用于地理加分")
    p.add_argument("--allow-remote", action="store_true", help="接受远程/异地")

    p = sub.add_parser("add-job", help="录入一个岗位")
    p.add_argument("--co", required=True, help="单位/公司")
    p.add_argument("--role", default="")
    p.add_argument("--city", default="")
    p.add_argument("--due", default="", help="截止日 YYYY-MM-DD")
    p.add_argument("--major-list", default="", help="公告里的专业名单原文，逗号分隔")
    p.add_argument("--notice-text", default="", help="公告里的专业描述段（含'等''以X类为主'等）")
    p.add_argument("--headcount", type=int, default=None, help="招聘人数")
    p.add_argument("--bachelor-ok", action="store_true", help="明确招本科")
    p.add_argument("--no-bachelor", action="store_true", help="明确不招本科")
    p.add_argument("--degree-min", default="本科", choices=["专科", "本科", "硕士", "博士"])
    p.add_argument("--family", default="", help="岗位族：后端/前端/算法/数据/测试/运维/嵌入式/实施…")
    p.add_argument("--stack", default="", help="技术栈，逗号分隔（不填则按岗位族取默认）")
    p.add_argument("--url", default="")
    p.add_argument("--note", default="")
    p.add_argument("--remote", action="store_true")

    sub.add_parser("list", help="列出已录岗位")

    p = sub.add_parser("check-major", help="专业口径风险判定")
    p.add_argument("--major", required=True)
    p.add_argument("--major-list", default="")
    p.add_argument("--notice-text", default="")

    p = sub.add_parser("score", help="五维打分")
    p.add_argument("--id", type=int, default=None, help="只算某个岗位")

    sub.add_parser("plan", help="投递计划（冲稳保+冲突）")

    p = sub.add_parser("tracker", help="生成离线台账 HTML")
    p.add_argument("--out", default="求职台账.html")
    p.add_argument("--name", default="")

    p = sub.add_parser("interview", help="模拟面试抽题")
    p.add_argument("--n", type=int, default=8)
    p.add_argument("--level", default="", help="L0/L1/L2/L3/L4，不填则混合")
    p.add_argument("--shuffle", action="store_true", help="随机抽题")
    p.add_argument("--answer", action="store_true", help="同时打印考察要点")

    sub.add_parser("review", help="复盘模板")
    return ap


def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)
    if not args.cmd:
        cmd_help(args)
        return 0
    fn = {
        "help": cmd_help, "init": cmd_init, "add-job": cmd_add_job, "list": cmd_list,
        "check-major": cmd_check_major, "score": cmd_score, "plan": cmd_plan,
        "tracker": cmd_tracker, "interview": cmd_interview, "review": cmd_review,
    }.get(args.cmd)
    if not fn:
        ap.print_help()
        return 1
    return fn(args) or 0


if __name__ == "__main__":
    sys.exit(main())
