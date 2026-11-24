# CHANGELOG · 求职台

## v2.0.0 — 2026-11-24（评审后补全）

### 评审结论（v1.0 的缺口）

| # | 缺口 | 严重度 | v2 处置 |
|---|---|---|---|
| 1 | 只有"建台账"，**没有筛岗**：凭什么判断一个 JD 值不值得投，没说 | 高 | 新增 `qiuzhi screen`：按画像与硬门槛批量筛 |
| 2 | **没有量化评分**：全程靠感觉排序 | 高 | 新增 `qiuzhi score`：五维规则打分 + 逐条扣分理由 |
| 3 | **没有投递建议**：不知道先投谁、冲稳保怎么配 | 高 | 新增 `qiuzhi plan`：冲/稳/保分层 + 时间冲突提示 |
| 4 | **面试环节只有评分标准，没有可执行的流程** | 中 | 新增 `qiuzhi interview`：抽题 + 追问 + 打分表模板 |
| 5 | **没有 help 入口**，用户不知道怎么调 | 高 | 新增 `qiuzhi help` 与 SKILL.md「指令表」 |
| 6 | 岗位族与计算机技术栈没有映射，跨岗位族无法比较 | 中 | 新增 `references/05-岗位族与技术栈矩阵.md` |
| 7 | 台账脚本是独立的，与画像/评分不联动 | 中 | `qiuzhi tracker` 统一调用，台账带评分列 |
| 8 | 专业口径核验只有人工步骤 | 中 | 新增 `qiuzhi check-major`：自动判高/中/低风险 |

### 新增文件

- `scripts/qiuzhi.py` — 统一 CLI，7 个子命令（help/init/add-job/screen/score/plan/tracker/check-major/interview/review）
- `scripts/make_tracker.py` — 保留，被 `qiuzhi tracker` 调用
- `references/05-岗位族与技术栈矩阵.md`
- `references/06-岗位评分模型.md`
- `references/07-投递策略与排序.md`

### 验收（可复现）

```bash
cd 能力层/技能库/qiuzhi-taibao/scripts
python3 qiuzhi.py help
python3 qiuzhi.py init --name 示例 --major 物联网工程 --degree 本科 --grad 2027 --cities 石家庄,成都 --skills Java,MySQL,Linux,Python
python3 qiuzhi.py add-job --co 国网河北省电力 --role 电子信息类 --city 石家庄 --due 2026-11-25 --major-list "计算机科学与技术,软件工程,网络与信息安全,人工智能" --notice-text "招聘专业指主修专业，以电工类专业为主" --bachelor-ok
python3 qiuzhi.py score
python3 qiuzhi.py plan
python3 qiuzhi.py tracker --out /tmp/台账.html
```

判据：三个命令都能跑出结果、score 给出五维分与总分、plan 输出冲稳保分层、tracker 生成 HTML 且含评分列。

## v3.1.0 — 2026-11-24（发给他人的可分发包）

全面评审后修的 10 项见 `docs/REVIEW-v3.1.md`。要点：

- **新增给人看的 `README.md`**：Windows 三步装、六个命令、三个典型场景、常见问题。此前只有给 AI 看的 SKILL.md。
- **新增 `安装-Windows.bat`**：双击即装（自动找 python / py），全英文提示避免 GBK 乱码，CRLF 换行。
- **新增 `scripts/package.py`**：打包自动排除 `data/`（个人数据）、`__pycache__`、`docs/`（内部评审），生成 SHA256SUMS。
- **`install.py` 增强**：Windows 路径探测与提示；命令正文路径统一写正斜杠（避免 Windows 反斜杠被当转义）；新增 `--check` 只校验；装后自检（技能文件数/命令数/能否定位技能包/占位符残留）。
- **示例数据改动态日期**：台账示例改"今天+1/+3/+5/+7 天"，不会过几天就全变逾期。
- **`plan.py --until` 自动推算**：不传就用"今年 4-30（已过则明年）"，非 2027 届也能用。
- **版本号统一**：`qiuzhi.py help` 从 VERSION 读取，不再写死。
- 新增 `VERSION`、`LICENSE`（MIT，可自由转发给同学）。

三道闸结果：查敏 0 命中；隔离目录解压后 `--check` 通过、安装成功（25 文件 / 13 命令 / 占位符无残留）、`plan.py` 与 `qiuzhi.py` 可运行；包内不含 docs 与 data。
