#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成「日计划 / 周计划」HTML（浅色科技蓝，可打印，离线单文件）。

用法:
    python3 plan.py --kind day  --out 今日计划.html
    python3 plan.py --kind week --out 周计划.html --until 2027-04-30
    python3 plan.py --kind day  --data-dir ../data --name 张三

数据来源（都可不填）:
    --data-dir 指向 skills 的数据目录（含 profile.json / jobs.json），用来把"截止临近/待确认"的岗位排进计划
    --items    额外的待办，分号分隔，如 "打电话确认专业口径；投国网四川"

设计原则：计划里每条都要能勾掉；不带空话；HTML 单文件、双击可看、Ctrl+P 可打印。
"""
import argparse
import datetime
import json
import os
import sys

CSS = """
:root{--bg:#f5f8fc;--card:#fff;--line:#e3eaf3;--ink:#1b2433;--ink2:#5b6b80;--blue:#2e5fa3;
--blue-l:#e8f0fb;--red:#c0392b;--red-l:#fdecea;--amber:#b7791f;--amber-l:#fdf5e6;--green:#1e7d4f;--green-l:#e6f5ee}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.65 -apple-system,"Segoe UI","Microsoft YaHei",sans-serif}
.wrap{max-width:900px;margin:0 auto;padding:22px 20px 60px}
header{margin-bottom:16px}
h1{font-size:22px;margin:0 0 4px}
.sub{color:var(--ink2);font-size:13px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin-bottom:14px}
.card h2{font-size:14px;margin:0 0 10px;color:var(--ink2)}
ul{margin:0;padding-left:20px}
li{margin:5px 0}
li.done{color:var(--ink2);text-decoration:line-through}
.tag{display:inline-block;padding:0 7px;border-radius:20px;font-size:12px;line-height:1.7}
.t-blue{background:var(--blue-l);color:var(--blue)}
.t-red{background:var(--red-l);color:var(--red)}
.t-amber{background:var(--amber-l);color:var(--amber)}
.t-green{background:var(--green-l);color:var(--green)}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--ink2);font-size:12px;background:#fbfdff;font-weight:600}
tr.phase td{background:var(--blue-l);color:var(--blue);font-weight:600;font-size:12px}
.phase-note{color:var(--ink2);font-size:12px;margin:4px 0 0}
footer{color:var(--ink2);font-size:12px;text-align:center;margin-top:22px}
@media print{.wrap{max-width:none;padding:0}.card{break-inside:avoid;border-color:#ccc}footer{display:none}}
@media (max-width:640px){.wrap{padding:14px}table{font-size:12px}th:nth-child(4),td:nth-child(4){display:none}}
"""


def esc(s):
    return (str(s if s is not None else '')
            .replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;'))


def load_json(p):
    if not p or not os.path.exists(p):
        return None
    try:
        with open(p, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def days_left(due):
    try:
        d = datetime.date.fromisoformat(due)
    except Exception:
        return None
    return (d - datetime.date.today()).days


def urgent_jobs(jobs):
    out = []
    for j in jobs or []:
        dl = days_left(j.get('due', ''))
        if dl is None:
            continue
        if dl < 0:
            continue
        if dl <= 7:
            out.append((dl, j))
    out.sort(key=lambda x: x[0])
    return out


# ------------------------------------------------------------------ 日计划
def build_day(args, profile, jobs):
    today = datetime.date.today()
    weekday = '一二三四五六日'[today.weekday()]
    items = [x.strip() for x in (args.items or '').split(';') if x.strip()]

    tasks = []
    for dl, j in urgent_jobs(jobs):
        tags = []
        if dl == 0:
            tags.append(('<span class="tag t-red">今天截止</span>', 0))
            tasks.append((0, '【今天截止】%s / %s → 立即提交，材料先备齐（学籍验证、成绩单、推荐表）'
                          % (j.get('co', ''), j.get('role', '')), 't-red'))
        else:
            tasks.append((dl, '【剩 %d 天】%s / %s → 今天把材料清单过一遍' % (dl, j.get('co', ''), j.get('role', '')), 't-amber'))

    for i in items:
        tasks.append((99, i, 't-blue'))

    if profile and profile.get('major'):
        tasks.append((98, '确认专业口径：把目标公告的专业名单与「%s」逐字比一遍，高风险就打公告电话'
                       % profile.get('major'), 't-blue'))
    if not tasks:
        tasks.append((99, '还没有待办：先去岗位库录 3 个岗位，或运行 /zhaogang 找岗位', 't-blue'))

    tasks.sort(key=lambda x: x[0])

    rows = ''.join('<li><span class="tag %s">%s</span></li>' % (cls, esc(txt)) for _, txt, cls in [
        (a, b, c) for a, b, c in tasks])

    blocks = [
        ('上午 9:00-11:30', '投递与确认（打电话、交材料、改简历针对性部分）'),
        ('下午 14:00-17:00', '面试准备（模拟面试 1 轮 + 复盘；补一个技术缺口）'),
        ('晚上 19:00-21:00', '信息刷新 20 分钟 + 刷题/项目 1 小时，剩下的休息'),
    ]
    block_html = ''.join('<tr><td>%s</td><td>%s</td></tr>' % (esc(a), esc(b)) for a, b in blocks)

    body = """
<header>
  <h1>今天该干什么 · %s 周%s</h1>
  <div class="sub">%s%s</div>
</header>
<div class="card">
  <h2>今日待办（做完就勾掉）</h2>
  <ul id="todo">%s</ul>
</div>
<div class="card">
  <h2>时间块建议</h2>
  <table><thead><tr><th style="width:150px">时段</th><th>干什么</th></tr></thead><tbody>%s</tbody></table>
  <p class="phase-note">原则：上午做有截止压力的事，下午做需要专注的（模拟面试/技术），晚上只做轻的。</p>
</div>
<div class="card">
  <h2>今天不要做的事</h2>
  <ul>
    <li>不要海投超过 3 个岗位——投了不跟等于没投</li>
    <li>不要在没确认专业口径前花一小时改简历</li>
    <li>不要刷招聘 App 超过 20 分钟（信息刷新 20 分钟封顶）</li>
  </ul>
</div>
<footer>生成于 %s · 点条目可勾掉（仅本页显示）· Ctrl+P 可打印</footer>
""" % (
        today.isoformat(), weekday,
        esc(args.name or (profile or {}).get('name') or ''),
        '｜' + esc(profile.get('major')) + ' / ' + esc(profile.get('degree', '')) if profile and profile.get('major') else '',
        rows, block_html, datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))

    js = """
document.querySelectorAll('#todo li').forEach(function(li){
  li.style.cursor='pointer';
  li.addEventListener('click',function(){li.classList.toggle('done');});
});
"""
    return body, js


# ------------------------------------------------------------------ 周计划
PHASES = [
    ('2026-11-24', '2026-11-30', '抢截止',
     '国网第一批、运营商、银行这一周集中截止。先打电话确认专业口径，再交材料。'),
    ('2026-12-01', '2026-12-31', '笔试月',
     '统一笔试集中在 12 月上中旬（国网初定 12/6）。考完立刻准备面试，别等成绩。'),
    ('2027-01-01', '2027-01-31', '寒假补短',
     '补两个最致命的技能缺口；把简历改成 3 个方向版本；准备春招提前批。'),
    ('2027-02-01', '2027-02-28', '二批开闸',
     '国网第二批、省考报名陆续开始；同时投互联网春招提前批。'),
    ('2027-03-01', '2027-03-31', '春招主战场',
     '省考联考笔试（下旬）、选调生、春招补录。这个月最忙，别接新项目。'),
    ('2027-04-01', '2027-04-30', '收尾定盘',
     '事业单位、三支一扶、补录；手上 offer 做决策，不再海投。'),
]


def build_week(args, profile, jobs):
    until = datetime.date.fromisoformat(args.until)
    start = datetime.date.today()
    # 对齐到本周一
    start = start - datetime.timedelta(days=start.weekday())

    rows = []
    for i, (p_from, p_to, title, note) in enumerate(PHASES):
        rows.append('<tr class="phase"><td colspan="4">%s ｜ %s ~ %s</td></tr>' % (esc(title), p_from, p_to))
        rows.append('<tr><td colspan="4" class="phase-note" style="color:#5b6b80;font-size:12px">%s</td></tr>' % esc(note))
        pf = datetime.date.fromisoformat(p_from)
        pt = datetime.date.fromisoformat(p_to)
        cur = max(pf, start)
        n = 1
        while cur <= pt and cur <= until:
            wk_end = min(cur + datetime.timedelta(days=6), pt, until)
            goal, acts = week_goal(cur, p_to)
            rows.append(
                '<tr><td>W%02d</td><td>%s ~ %s</td><td>%s</td><td>%s</td></tr>'
                % (i * 6 + n, cur.strftime('%m-%d'), wk_end.strftime('%m-%d'), esc(goal), esc(acts)))
            cur = wk_end + datetime.timedelta(days=1)
            n += 1

    urgent = urgent_jobs(jobs)[:6]
    urgent_html = ''.join(
        '<li>【剩 %d 天】%s / %s（%s）</li>' % (dl, esc(j.get('co', '')), esc(j.get('role', '')), esc(j.get('due', '')))
        for dl, j in urgent) or '<li>暂无 7 天内截止的岗位</li>'

    body = """
<header>
  <h1>求职周计划 · 本周起到 %s</h1>
  <div class="sub">%s%s ｜ 生成于 %s</div>
</header>
<div class="card">
  <h2>这 7 天必做</h2>
  <ul>%s</ul>
  <p class="phase-note">每周只给自己 3 个硬任务：投 2 家「冲」+ 1 家「保」；练 1 轮模拟面试；补 1 个技术缺口。</p>
</div>
<div class="card">
  <h2>逐周排期</h2>
  <table>
    <thead><tr><th style="width:60px">周次</th><th style="width:110px">日期</th><th style="width:180px">阶段目标</th><th>关键动作</th></tr></thead>
    <tbody>%s</tbody>
  </table>
</div>
<div class="card">
  <h2>每周固定动作（打印贴在桌上）</h2>
  <ul>
    <li>周一：刷新信息源 20 分钟（招聘平台 / 校就业网 / 省人事考试网），只记录不投</li>
    <li>周二-周三：投「冲」1 家（定制简历 40 分钟）</li>
    <li>周四：投「稳」2 家（标准简历各 15 分钟）+ 跟进上周投递</li>
    <li>周五：投「保」1 家；整理本周复盘</li>
    <li>周末：模拟面试 1 轮 + 补技能缺口</li>
  </ul>
  <p class="phase-note">提醒：笔试撞车时只能选一家考，第一志愿填最想去的。</p>
</div>
<footer>生成于 %s · Ctrl+P 可打印成 A4</footer>
""" % (
        until.isoformat(),
        esc(args.name or (profile or {}).get('name') or ''),
        '｜' + esc(profile.get('major')) if profile and profile.get('major') else '',
        datetime.date.today().isoformat(),
        urgent_html, ''.join(rows), datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))

    return body, ""


def week_goal(cur, phase_to):
    """按日期给该周的目标与关键动作（规则化，不需要模型）。"""
    m = cur.month
    if m == 11:
        return '抢截止 + 定方向', '确认专业口径电话；交国网/银行/运营商材料；建立投递台账'
    if m == 12:
        return '笔试冲刺', '统一笔试（国网初定12/6）；每场考完当天复盘；开始准备技术面'
    if m == 1:
        return '补短板', '补两个技能缺口（按评分里的缺口技能）；简历三版定稿；春招提前批开投'
    if m == 2:
        return '二批与省考报名', '国网二批报名；省考报名与刷题；互联网春招投递'
    if m == 3:
        return '春招主战场', '省考联考笔试；选调生；春招集中面试；每周 2 轮模拟面试'
    if m == 4:
        return '收尾与决策', '事业单位/三支一扶/补录；offer 五维比较；不再海投'
    return '常规推进', '按周节奏投递与面试'


def main():
    ap = argparse.ArgumentParser(description='生成日计划/周计划 HTML')
    ap.add_argument('--kind', choices=['day', 'week'], required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--data-dir', default='')
    ap.add_argument('--items', default='', help='额外待办，分号分隔')
    ap.add_argument('--name', default='')
    ap.add_argument('--until', default='', help='默认自动：毕业年 4 月 30 日（取不到则今年/明年 4-30）')
    args = ap.parse_args()

    if not args.until:
        td = datetime.date.today()
        y = td.year if td <= datetime.date(td.year, 4, 30) else td.year + 1
        args.until = '%d-04-30' % y
        print('未指定 --until，自动用 %s' % args.until)

    profile, jobs = None, []
    if args.data_dir:
        profile = load_json(os.path.join(args.data_dir, 'profile.json'))
        j = load_json(os.path.join(args.data_dir, 'jobs.json'))
        if isinstance(j, list):
            jobs = j

    if args.kind == 'day':
        body, js = build_day(args, profile, jobs)
        title = '今日计划'
    else:
        body, js = build_week(args, profile, jobs)
        title = '求职周计划'

    html = ('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s · %s</title><style>%s</style></head><body><div class="wrap">%s</div>'
            '<script>%s</script></body></html>' % (title, esc(args.name or '求职'), CSS, body, js))

    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print('已生成: %s (%.1f KB)' % (out, len(html.encode()) / 1024))
    return 0


if __name__ == '__main__':
    sys.exit(main())
