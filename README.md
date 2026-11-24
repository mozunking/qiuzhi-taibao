# 求职台 · Qoder 求职技能包

> 给**计算机类应届本科生**的求职工作台。装进 Qoder 后，对话框里多出六个斜杠命令：找岗位、模拟面试、改简历、查公司、日计划、周计划。
> 纯本地运行，不联网上传，零第三方依赖（只要 Python 3.8+）。

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](#环境要求)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Qoder](https://img.shields.io/badge/Qoder-Skills%20%2B%20Commands-2E5FA3)](https://docs.qoder.com/zh/extensions/skills)
[![No Telemetry](https://img.shields.io/badge/telemetry-none-success.svg)](#隐私)

它不是又一个"投递进度表格"，而是把求职拆成**能算、能查、能打印**的六件事：

- **找岗位**时告诉你这个岗位到底认不认你的专业（专业口径逐字核验，这是最容易翻车的一步）
- **给岗位打分**：技术栈 30 + 经历 20 + 成长性 20 + 上岸概率 20 + 地理 10，附每条扣分理由
- **改简历**只改表达不改事实，逐条给「改前 → 改后 → 为什么」
- **模拟面试**一次一题、三层追问、五维打分，结束出复盘表
- **日/周计划**生成可打印的 HTML，周计划一路排到毕业年 4 月底

---

## 目录

- [30 秒快速开始](#30-秒快速开始)
- [六个命令](#六个命令)
- [它到底解决了什么问题](#它到底解决了什么问题)
- [评分模型](#评分模型)
- [命令行工具](#命令行工具)
- [项目结构](#项目结构)
- [隐私](#隐私)
- [常见问题](#常见问题)
- [参与贡献](#参与贡献)
- [License](#license)

---

## 30 秒快速开始

### Windows

1. 确认有 Python 3.8+：`cmd` 里敲 `python --version`（没有就去 [python.org](https://www.python.org/downloads/) 装，**勾选 Add python.exe to PATH**）
2. 下载本仓库（`Code` → `Download ZIP`）并解压
3. 双击 **`安装-Windows.bat`**

### macOS / Linux

```bash
git clone https://github.com/mozunking/qiuzhi-taibao.git
cd qiuzhi-taibao
python3 scripts/install.py
```

看到这样的输出就成功了：

```
[OK] /Users/you/.qoder
     技能 → /Users/you/.qoder/skills/qiuzhi-taibao（25 文件）
     命令 → /Users/you/.qoder/commands（13 个）
     自检 → 命令可定位技能包：是｜占位符残留：无
```

**重启 Qoder**，在对话框输入 `/`，就能看到命令。先跑 `/qiuzhi`。

> 只验证不安装：`python3 scripts/install.py --check`
> 装到某个项目（项目级生效）：`python3 scripts/install.py --target .qoder`

---

## 六个命令

| 命令 | 英文别名 | 干什么 | 产出 |
|---|---|---|---|
| `/qiuzhi` | — | 总览 + 首次使用三步 | 一屏说明 |
| `/zhaogang` | `/find-jobs` | 按专业与城市搜真实岗位，标专业口径风险 | 岗位表 + 本周先投 3 个 |
| `/mianshi` | `/mock-interview` | 一次一题、三层追问、五维打分 | 复盘表 + gap 清单 |
| `/jianli` | `/resume-fix` | 按 JD 逐条改简历 | 改前/改后/为什么 |
| `/gongsi` | `/company-check` | 面试前 10 行看透一家单位 | 情报卡 + 该问 HR 的问题 |
| `/rijihua` | `/day-plan` | 今天该干什么 | 可勾选可打印的 HTML |
| `/zhoujihua` | `/week-plan` | 排到毕业年 4 月底 | 逐周计划 HTML |

命令名按 Qoder 规范只能是英文小写字母，因此**用拼音当主名、英文作别名**，两种都能输入。

### 典型场景

**刚开始，什么都没有**
```
/qiuzhi      → 看总览
（回答：专业全名 / 哪届 / 想去哪些城市）
/zhaogang    → 出一批可投岗位
/rijihua     → 定今天干什么
```

**有岗位要投，简历没底**
```
/jianli      → 给 JD + 简历，逐条改
/gongsi 国网四川 → 投之前先搞清楚对方是干什么的
```

**收到面试通知**
```
/gongsi 公司名   → 10 分钟摸清底细
/mianshi         → 真强度模拟一场
/zhoujihua       → 把面试排进周计划
```

---

## 它到底解决了什么问题

求职里最容易翻车的不是"面试答不好"，而是这三件事没人讲清楚：

### 1. 你的专业到底算不算

招聘公告的「主要招聘专业」是**封闭列举**，资格审查按学信网专业全名逐字比。名字不在里面，简历在初审就被刷，而且不通知理由。

同一个专业还有两套口径，混着说就会给出错答案：

| 口径 | 谁定的 | 用在哪 | 物联网工程落在哪 |
|---|---|---|---|
| 考试分类 | 统一笔试大纲按专业大类出卷 | 决定你考哪套卷 | **计算机类**（考计算机卷，通信类是另一套） |
| 公告招录类别 | 公告把"计算机类+通信类"合并写作"电子信息类" | 决定你能不能投 | 归在**电子信息类**这个筐 |

所以正确的问法不是"我属于哪一类"，而是**"公告那份名单里有没有点我的专业名"**。技能里的 `check-major` 就是判这个，并给出能直接照着念的电话话术。

### 2. 本科的真实定位

| 事实 | 影响 |
|---|---|
| AI 替代初级编码 | 只会 CRUD 不再是技能 |
| 岗位总量收缩、应届生多 | 同一岗位竞争者更多 |
| 本科岗位向两端集中 | 一端运维/测试/实施/嵌软，一端算法（但算法基本要硕士） |

**本科真实能打的四类**：工程实现（后端/前端/客户端/嵌入式）、质量与稳定（测开/运维/实施）、行业信息化（电力/医疗/金融/制造 IT）、特殊通道（选调/军队文职/三支一扶）。
**不建议死磕**：算法研究岗、芯片前端设计、大厂核心架构岗——不是不能，是概率太低，别当主投。

### 3. 措施要能数

- **多投**：每周 2 家主投 + 1 家冲刺，累计 **30–50 家**。低于 30 家样本不够；高于 60 家没转化，是简历或定位有问题
- **多面**：每 2 周至少 1 场真实面试或 1 轮模拟。一个月没面试 = 简历过不了筛，问题不在面试
- **城市**：二线优先——成都、苏州、武汉、西安、合肥。竞争约一线一半，薪资约 60-70%

---

## 评分模型

```
技术栈匹配 30 + 经历证据 20 + 岗位成长性 20 + 上岸概率 20 + 地理与生活 10
专业口径高风险 −15 ｜ 异地 −5

≥80 冲 ｜ 65–79 稳 ｜ 50–64 保 ｜ <50 不建议
学历不够 → 不可投 ｜ 已截止 → 过期
```

**分数是排序工具，不是判决**。重点看每条扣分理由——尤其"技能缺口"和"专业口径未确认"这两条。
两条已知局限：技能靠关键词匹配、看不出深度；模型不知道你讨厌什么岗位，你的意愿优先级高于分数。

细节见 [`references/06-岗位评分模型.md`](references/06-岗位评分模型.md)。

---

## 命令行工具

不装 Qoder 也能用（能装 Python 就行）：

```bash
# 建画像
python3 scripts/qiuzhi.py init --major 物联网工程 --degree 本科 --grad 2027 \
    --cities 石家庄,成都 --skills Java,MySQL,Linux --projects 2 --intern

# 录岗位（--major-list 必须是公告原文）
python3 scripts/qiuzhi.py add-job --co 国网四川省电力 --role 电子信息类 \
    --due 2027-03-15 --major-list "计算机科学与技术,通信工程" --bachelor-ok --headcount 1140 --family 后端

# 判专业口径 / 打分 / 出投递计划
python3 scripts/qiuzhi.py check-major --major 物联网工程 --major-list "计算机科学与技术,软件工程"
python3 scripts/qiuzhi.py score
python3 scripts/qiuzhi.py plan

# 离线台账（单文件 HTML，双击打开）
python3 scripts/qiuzhi.py tracker --out 求职台账.html

# 日计划 / 周计划
python3 scripts/plan.py --kind day  --out 今日计划.html
python3 scripts/plan.py --kind week --out 求职周计划.html     # 默认排到毕业年 4-30
```

`python3 scripts/qiuzhi.py help` 看全部子命令。

---

## 项目结构

```
.
├── SKILL.md                  Qoder 技能本体（AI 读的说明书）
├── README.md                 人读的（你在看的）
├── commands/                 13 个斜杠命令（install.py 复制到 Qoder）
├── scripts/
│   ├── install.py            安装器（--check 只校验）
│   ├── qiuzhi.py             筛岗/评分/计划/台账/面试（十个子命令）
│   ├── plan.py               日计划/周计划 HTML 生成器
│   ├── make_tracker.py       离线投递台账生成器
│   ├── make_commands.py      重新生成 commands/*.md（改内容后跑一次）
│   └── package.py            打成可分发的 zip（排除 data/）
├── references/               11 篇方法论
│   ├── 01-求职时间线.md
│   ├── 02-题库与评分标准.md
│   ├── 03-央企国企专业口径核验.md
│   ├── 04-JD解析与简历对齐.md
│   ├── 05-岗位族与技术栈矩阵.md
│   ├── 06-岗位评分模型.md
│   ├── 07-投递策略与排序.md
│   ├── 08-公司调研清单.md
│   ├── 09-岗位渠道与平台清单.md
│   └── 10-行情与本科定位.md
├── assets/复盘表模板.md
└── VERSION / LICENSE / CHANGELOG.md
```

---

## 隐私

- 所有数据存在本地 `~/.qoder/skills/qiuzhi-taibao/data/`（`profile.json` 画像、`jobs.json` 岗位）
- 脚本**不发任何网络请求**，不采集遥测
- 换电脑：把 `data/` 目录拷过去
- 仓库里不含任何个人数据；`data/` 已在 `.gitignore` 中

---

## 常见问题

**装了但 `/` 里看不到命令**
重启 Qoder；或在 Qoder 里执行 `/commands` 重新加载。

**报"没找到 Qoder 配置目录"**
先正常启动一次 Qoder 让它生成配置，再装；或手动指定：
`python scripts/install.py --target "C:\Users\你的用户名\.qoder"`

**`python` 不是内部或外部命令**
Python 没装或没加 PATH。重装时勾选 "Add python.exe to PATH"。

**能不能不装、直接用**
可以。把 `SKILL.md` 拖进对话，说"按这个技能帮我找工作"，效果一样；命令只是快捷方式。

**支持哪些 AI 工具**
技能本体是通用 Markdown + Python 脚本，Claude Code / Cursor / CodeBuddy 等支持 agent skills 或规则文件的环境也能用，命令目录结构按需调整。

---

## 参与贡献

欢迎 PR。常见改动：

- **补题库**：改 `scripts/qiuzhi.py` 里的 `BANK` 列表（格式 `{level, q, focus}`，L0–L4 各留位置）
- **补岗位族/渠道/行情**：改 `references/` 下对应文件
- **改命令提示词**：改 `scripts/make_commands.py`，然后 `python3 scripts/make_commands.py` 重新生成
- **改完自测**：`python3 scripts/install.py --check` 必须通过

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

**请注意**：新增招聘信息类内容必须带出处；不要提交任何真实个人简历或岗位数据。

---

## License

[MIT](LICENSE) —— 可自由使用、修改、转发给同学；请勿转售。
