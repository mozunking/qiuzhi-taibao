---
name: 求职台
description: 计算机类应届本科生的求职工作台。六个斜杠命令覆盖找岗位、模拟面试、改简历、查公司、日计划、周计划；配套本地评分引擎与离线台账。触发词：求职、找工作、秋招、春招、校招、投递、简历、模拟面试、面经、查公司、offer比较、日计划、周计划、专业能不能报、央国企、国网、选调、岗位匹配、多投多面。产出：可投岗位清单（带专业口径风险）+ 简历改写清单 + 面试复盘表 + 可打印的日/周计划 HTML。
description_zh: 求职台 v3：六个斜杠命令（找岗位/模拟面试/改简历/查公司/日计划/周计划，支持拼音）＋评分引擎＋离线台账；面向计算机类应届本科，含行情约束与二线城市策略
description_en: Job-hunting workbench for CS graduates - six slash commands (find jobs, mock interview, resume, company check, daily/weekly plan) plus local scoring and offline tracker.
version: 3.1.0
---

# 求职台（qiuzhi-taibao）v3.0

给**计算机类应届本科生**用。核心是六个斜杠命令 + 一套本地工具，让人少想、直接做。

## 零、给别人装（发给同学用）

这个包可以直接压缩发给别人。对方解压后：

- **Windows**：双击 `安装-Windows.bat`（脚本会自己找 python）
- **macOS / Linux**：`python3 scripts/install.py`

装之前想先验证包是否完整：`python3 scripts/install.py --check`。
打新包：`python3 scripts/package.py`（自动排除 data/ 个人数据，生成 SHA256SUMS）。

给「人」看的说明在 `README.md`，给「AI」看的说明是本文件——两者不要混。

## 一、先装（30 秒）

```bash
python3 scripts/install.py            # 自动检测 ~/.qoder 或 ~/.qoder-cn
python3 scripts/install.py --dry-run  # 只看会写哪些文件
python3 scripts/install.py --target .qoder   # 装到当前项目
```

装完重启 Qoder，对话框输入 `/` 就能看到六个命令（及英文别名）。**先跑 `/qiuzhi` 看总览。**

> 没装也行：直接说"帮我找工作 / 模拟面试 / 改简历"，本技能会自动触发，效果一样。

## 二、六个命令

| 命令 | 英文别名 | 干什么 | 产物 |
|---|---|---|---|
| `/qiuzhi` | — | 总览 + 首次使用三步 | 一屏说明 |
| `/zhaogang` | `/find-jobs` | 按专业与城市搜真实可投岗位，标专业口径风险 | 岗位表 + 本周先投 3 个 |
| `/mianshi` | `/mock-interview` | 真实强度模拟面试：一次一题 + 三层追问 + 五维打分 | 复盘表 + gap 清单 |
| `/jianli` | `/resume-fix` | 按 JD 逐条改简历，只改表达不改事实 | 改前/改后/为什么 清单 |
| `/gongsi` | `/company-check` | 面试前 10 行看透一家单位 | 情报卡 + 该问 HR 的问题 |
| `/rijihua` | `/day-plan` | 今天该干什么 | 可勾选、可打印的 HTML |
| `/zhoujihua` | `/week-plan` | 从本周排到 2027-04-30 | 逐周计划 HTML |

命令名按 Qoder 规范只能是英文小写字母，所以用**拼音当主名**、英文作别名，两种都能输。

## 三、把现实先摆出来（防止幻想）

| 事实 | 对本科生的影响 |
|---|---|
| AI 替代初级编码 | 只会 CRUD 不再是技能 |
| 岗位总量收缩、应届生多 | 同一个岗位竞争者更多 |
| 本科岗位向两端集中 | 一端运维/测试/实施/嵌软，一端算法（但算法基本要硕士） |

**本科真实能打的四类**：工程实现（后端/前端/客户端/嵌入式）、质量与稳定（测开/运维/实施）、行业信息化（电力/医疗/金融/制造 IT）、特殊通道（选调/军队文职/三支一扶）。
**不建议死磕**：算法研究岗、芯片前端设计、大厂核心架构岗——不是不能，是概率太低，别当主投。

## 四、措施要能数（这是给人的行为准则）

- **多投**：每周 2 家主投 + 1 家冲刺；累计 **30–50 家**。低于 30 家样本不够，高于 60 家没转化就是简历或定位有问题。
- **多面**：每 2 周至少 1 场真实面试或 1 轮模拟面试。一个月没面试 = 简历过不了筛，问题不在面试。
- **城市**：二线优先——成都（游戏/军工/国网西南）、苏州（制造业软件/外企）、武汉（通信/光谷）、西安（军工院所）、合肥（AI/新能源）。竞争约一线一半，薪资约 60-70%，用三年换确定性。

详见 `references/10-行情与本科定位.md`、`references/09-岗位渠道与平台清单.md`。

## 五、五类方向（定大方向用，别按公司名气分）

| 大类 | 进入方式 | 本质 | 适合谁 |
|---|---|---|---|
| 编制类 | 国考/省考/选调/事业编/军队文职 | 有编制，技术荒废 | 求稳、本地 |
| 央国企类 | 电网/运营商/银行科技/军工院所 | 类编制，福利好，成长慢 | 想稳又想碰技术 |
| 市场化企业类 | 大厂/中厂/外企，提前批6-8月、秋招7-11月、春招3-4月 | 能力定价，技术积累快 | 真喜欢写代码 |
| 中小民企与外包 | 投简历即面，全年滚动 | 先就业后择业，驻场慎入 | 急需入职 |
| **国际化与出海** | 外企在华研发 / 中国公司出海岗 / 海外直投 | 英语+驻外，薪资高 | 英语好、能长期驻外、家里支持 |

国际化方向先过三关：英语能否开会、能否长期驻外、家里是否支持。一条不行就别投。

## 五半、依赖与示例 prompt

**依赖声明（写清，免得别人以为要装一堆东西）**
- 纯对话用法（改简历 / 模拟面试 / 查公司 / 找岗位）**不需要装任何东西**，只要模型能读本文件与 `references/`。
- 需要 **Python 3.8+（仅标准库）** 的只有三件事：生成台账或日周计划 HTML（`plan.py` / `make_tracker.py`）、命令行打分（`qiuzhi.py`）、装进 Qoder（`install.py`）。
- **零第三方包、零网络请求、无需数据库**。数据落在 `data/` 下两个 JSON。

**示例 prompt（别人不知道怎么开口时，直接让他照抄）**
`examples/` 下有 5 篇可直接粘贴的对话示例：
`01-找岗位.md`、`02-模拟面试.md`、`03-改简历.md`、`04-查公司.md`、`05-计划.md`。
用户说"我不知道怎么跟你说"时，先给对应那篇的第一段，不要解释一堆。

## 六、红线

1. **专业口径逐字核**，不许用"我属于某大类所以能报"下结论。用 `/zhaogang` 或 `check-major` 判风险，高风险必须给电话话术并让人打。
2. **不编招聘信息**：截止时间、名额必须有出处；核不到写"见官网"。
3. **不做自动投递、不代填网申、不碰账号**。
4. **付费内推、保 offer 一律当骗局**，不评估"靠不靠谱"。
5. **数据不出本机**（台账与简历只落本地）。
6. **分数是排序工具不是判决**：给分必须同时给扣分理由，并提醒"同分不同质"。

## 七、配套工具（命令行）

```bash
python3 scripts/qiuzhi.py help                 # 十个子命令（init/add-job/score/plan/tracker/interview/review…）
python3 scripts/qiuzhi.py init --major 物联网工程 --degree 本科 --grad 2027 --cities 石家庄,成都 --skills Java,MySQL
python3 scripts/qiuzhi.py add-job --co 国网四川 --role 电子信息类 --due 2026-11-25 --major-list "计算机科学与技术" --bachelor-ok
python3 scripts/qiuzhi.py score && python3 scripts/qiuzhi.py plan
python3 scripts/qiuzhi.py tracker --out 台账.html
python3 scripts/plan.py --kind day  --out 今日计划.html
python3 scripts/plan.py --kind week --until 2027-04-30 --out 周计划.html
```

评分：技术栈 30 + 经历 20 + 成长性 20 + 上岸 20 + 地理 10；专业高风险 −15、异地 −5。≥80 冲 / 65–79 稳 / 50–64 保 / <50 不建议。

## 八、文件地图

```
SKILL.md                  本文件
commands/*.md             13 个斜杠命令（6 主名 + 6 英文别名 + 1 总览），由 scripts/make_commands.py 生成
scripts/install.py        装进 Qoder（技能 + 命令）
scripts/qiuzhi.py         十个子命令：筛岗/评分/计划/台账/面试
scripts/plan.py           日计划 / 周计划 HTML 生成器
scripts/make_commands.py  重新生成命令文件
scripts/make_tracker.py   离线投递台账生成器
references/01~10          时间线 / 题库评分 / 专业口径 / JD对齐 / 岗位族 / 评分模型 / 投递策略 / 公司调研 / 渠道平台 / 行情定位
assets/复盘表模板.md
```

## 九、反面清单

- 拿"XX 专业属于计算机大类"直接回答"能不能报"。
- 只报分数不说扣分理由；给没出处的截止日期。
- 推荐付费内推；一次列二十个方向让人挑。
- 只给建议不给能跑的工具。
