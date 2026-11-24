# 参与贡献

感谢你愿意改进它。这个项目的目标是**让一个不懂技术的应届生能在 10 分钟内装好并真的用起来**，所以任何改动都请先问一句：这会让第一次用的人更容易，还是更难？

## 你可以贡献什么

| 类型 | 改哪里 | 注意 |
|---|---|---|
| 补充面试题库 | `scripts/qiuzhi.py` 里的 `BANK` 列表 | 格式 `{level, q, focus}`，L0–L4 各留位置 |
| 补充岗位族与技术栈 | `references/05-岗位族与技术栈矩阵.md` + `scripts/qiuzhi.py` 的 `FAMILY_STACK` | 两处要一起改，否则评分会取不到默认栈 |
| 补充渠道/平台 | `references/09-岗位渠道与平台清单.md` | 只写真实在用的，注明适合什么 |
| 修正行情与定位判断 | `references/10-行情与本科定位.md` | 带年份与来源，别写"我觉得" |
| 改斜杠命令的提示词 | `scripts/make_commands.py`，然后跑 `python3 scripts/make_commands.py` | **不要手改 `commands/*.md`**，它们由脚本生成 |
| 修 bug | 对应脚本 | 附复现步骤 |

## 提 PR 前请自测

```bash
python3 scripts/install.py --check      # 必须通过（退出码 0）
python3 scripts/make_commands.py        # 改过提示词就跑
python3 scripts/qiuzhi.py help          # 能正常打印
python3 scripts/plan.py --kind day --out /tmp/d.html   # 能生成 HTML
python3 scripts/install.py --target /tmp/fakeq         # 装到临时目录看是否成功
```

Windows 上对应把 `python3` 换成 `python`。

## 代码约定

- **只用 Python 标准库**。加第三方依赖会让"双击安装"这个前提失效。
- **不写死路径**。任何路径都从 `__file__` 推，或走参数。
- **不写死日期**。示例数据用相对日期（`今天+N`），否则过几天就全变"已逾期"。
- 中文文案直接写中文，不要为了 ASCII 牺牲可读性。
- Python 字符串里 `%` 要写成 `%%`（用了 `%` 格式化时）；f-string 里写 `{变量}` 前先确认变量存在。

## 不要提交的东西

- **任何真实个人数据**：简历、画像、岗位清单、手机号、邮箱、公司内部信息
- `data/` 目录（已在 `.gitignore`）
- 打包产物 `dist/`、`*.zip`
- 来源不明的招聘信息或面经

## 招聘信息类内容的硬要求

涉及具体单位的招聘条件（截止时间、名额、专业名单）时：

1. 必须有出处（公告原文链接或平台名）
2. 不许推测日期
3. 标注"自 YYYY-MM 公告"，因为下一批就会变

## Commit 信息

一行说清改了什么，中英文都行：

```
fix: 修正 plan.py 在 2 月时的周数计算
feat: 题库新增 L3 分布式相关 6 题
docs: 补充国网专业口径的两个口径说明
```

## 行为准则

- 不推荐付费内推、保 offer 服务，也不为这类服务做评估
- 不引导自动投递、绕过验证码或爬取登录态数据
- 对他人的学校、专业、家庭条件不作评价
