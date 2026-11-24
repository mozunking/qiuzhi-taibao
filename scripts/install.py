#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把「求职台」装进 Qoder：技能包 + 十三个斜杠命令。

在 Windows / macOS / Linux 上都能用，只需要 Python 3.8+（不需要装任何第三方库）。

用法：
    python install.py                   自动检测 Qoder 目录并安装
    python install.py --check           只校验文件与命令格式，不写任何东西
    python install.py --dry-run         只看会写哪些文件
    python install.py --target .qoder   装到当前项目（项目级）
    python install.py --target ~/.qoder 指定目标

Windows 上更简单：双击包里的「安装-Windows.bat」。

装完在 Qoder 对话框输入 / 就能看到：qiuzhi、zhaogang、mianshi、jianli、gongsi、rijihua、zhoujihua（及英文别名）。
"""
import argparse
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(HERE)
SKILL_NAME = "qiuzhi-taibao"
PLACEHOLDER = "{SKILL_DIR}"

NAME_RE = re.compile(r"^[a-z0-9_-]{1,100}$")
EXCLUDE_DIRS = {"data", "__pycache__", ".git", "node_modules", ".idea", ".vscode"}


def home_candidates():
    """返回可能存在的 Qoder 配置目录（跨平台）。"""
    home = os.path.expanduser("~")
    return [
        os.path.join(home, ".qoder"),      # Qoder IDE / CLI（Win: C:\Users\x\.qoder）
        os.path.join(home, ".qoder-cn"),   # Qoder CN CLI
        os.path.join(home, ".cursor"),     # Cursor（同为 agent 目录结构，容错用）
    ][:2]


def detect_targets(explicit):
    if explicit:
        return [os.path.abspath(os.path.expanduser(explicit))]
    return [p for p in home_candidates() if os.path.isdir(p)]


def collect_skill_files():
    out = []
    for root, dirs, files in os.walk(SKILL_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if f.endswith((".pyc", ".log", ".bak", ".DS_Store")):
                continue
            rel = os.path.relpath(os.path.join(root, f), SKILL_ROOT)
            if rel.startswith("commands" + os.sep) or rel.startswith("docs" + os.sep):
                continue  # 命令单独装；docs 是给人看的评审文档，不装
            out.append(rel)
    return sorted(out)


def check_command_files(cmd_dir):
    problems = []
    if not os.path.isdir(cmd_dir):
        return ["命令目录不存在: " + cmd_dir]
    seen = {}
    files = [f for f in sorted(os.listdir(cmd_dir)) if f.endswith(".md")]
    for f in files:
        p = os.path.join(cmd_dir, f)
        txt = open(p, encoding="utf-8").read()
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", txt, re.S)
        if not m:
            problems.append(f"{f}: 缺 frontmatter（--- 包裹）")
            continue
        head, body = m.group(1), m.group(2).strip()
        nm = re.search(r"^name:\s*(.+)$", head, re.M)
        ds = re.search(r"^description:\s*(.+)$", head, re.M)
        if not nm:
            problems.append(f"{f}: 缺 name")
        else:
            name = nm.group(1).strip()
            base = os.path.splitext(f)[0]
            if not NAME_RE.match(name):
                problems.append(f"{f}: name「{name}」不合规（只允许小写字母/数字/连字符/下划线）")
            if name != base:
                problems.append(f"{f}: name 与文件名不一致（{name} vs {base}）")
            if name in seen:
                problems.append(f"{f}: name 与 {seen[name]} 重复")
            seen[name] = f
        if not ds or len(ds.group(1).strip()) < 10:
            problems.append(f"{f}: description 缺失或过短")
        if len(body) < 80:
            problems.append(f"{f}: 正文过短（{len(body)} 字符）")
        if PLACEHOLDER not in body:
            problems.append(f"{f}: 正文缺少 {PLACEHOLDER} 占位符")
    if len(files) < 6:
        problems.append(f"命令只有 {len(files)} 个，少于 6 个（是不是没跑 make_commands.py？）")
    return problems


def do_check():
    problems = []
    need = ["SKILL.md", "README.md", "VERSION", os.path.join("scripts", "qiuzhi.py"),
            os.path.join("scripts", "plan.py"), os.path.join("commands", "qiuzhi.md")]
    for n in need:
        if not os.path.exists(os.path.join(SKILL_ROOT, n)):
            problems.append("缺文件: " + n)
    problems += check_command_files(os.path.join(SKILL_ROOT, "commands"))
    files = collect_skill_files()
    print(f"技能文件 {len(files)} 个｜命令 {len([f for f in os.listdir(os.path.join(SKILL_ROOT,'commands')) if f.endswith('.md')])} 个")
    if problems:
        print("校验不通过：")
        for p in problems:
            print("  ✗ " + p)
        return problems
    print("校验通过 ✓")
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true", help="只校验，不安装")
    args = ap.parse_args()

    if sys.version_info < (3, 8):
        print("[ERR] 需要 Python 3.8 以上，当前 %s" % sys.version.split()[0])
        return 2

    if args.check:
        return 0 if not do_check() else 2

    problems = do_check()
    if problems:
        return 2

    targets = detect_targets(args.target)
    if not targets:
        print("[ERR] 没找到 Qoder 配置目录。")
        print("      已查找: %s" % " / ".join(home_candidates()))
        print("      请先启动过一次 Qoder 让它生成配置目录，或用 --target 指定：")
        print("        python install.py --target \"%s\"" % os.path.join(os.path.expanduser("~"), ".qoder"))
        print("      想装到某个项目里：进项目目录后 python install.py --target .qoder")
        return 2

    files = collect_skill_files()
    cmd_src = os.path.join(SKILL_ROOT, "commands")
    n_cmd = len([f for f in os.listdir(cmd_src) if f.endswith(".md")])

    print("技能包 %s v%s" % (SKILL_NAME, open(os.path.join(SKILL_ROOT, "VERSION")).read().strip()
                          if os.path.exists(os.path.join(SKILL_ROOT, "VERSION")) else "?"))
    print("技能文件 %d 个｜命令 %d 个" % (len(files), n_cmd))

    if args.dry_run:
        for t in targets:
            print("  [dry-run] 将写入 %s 与 %s" % (os.path.join(t, "skills", SKILL_NAME), os.path.join(t, "commands")))
        return 0

    for t in targets:
        skill_dst = os.path.join(t, "skills", SKILL_NAME)
        if os.path.isdir(skill_dst):
            shutil.rmtree(skill_dst)
        for rel in files:
            dst = os.path.join(skill_dst, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(SKILL_ROOT, rel), dst)

        cmd_dst = os.path.join(t, "commands")
        os.makedirs(cmd_dst, exist_ok=True)
        # 写入时统一用正斜杠：Windows 反斜杠在 Markdown 里容易被当转义
        posix_skill = skill_dst.replace("\\", "/")
        for f in sorted(os.listdir(cmd_src)):
            if not f.endswith(".md"):
                continue
            txt = open(os.path.join(cmd_src, f), encoding="utf-8").read().replace(PLACEHOLDER, posix_skill)
            with open(os.path.join(cmd_dst, f), "w", encoding="utf-8") as fh:
                fh.write(txt)

        # 装后自检
        installed = len([x for x in os.listdir(cmd_dst) if x.endswith(".md")])
        probe = open(os.path.join(cmd_dst, "zhaogang.md"), encoding="utf-8").read()
        ok_path = posix_skill in probe and PLACEHOLDER not in probe
        skill_files = sum(len(fs) for _, _, fs in os.walk(skill_dst))
        print("[OK] %s" % t)
        print("     技能 → %s（%d 文件）" % (skill_dst, skill_files))
        print("     命令 → %s（%d 个）" % (cmd_dst, installed))
        print("     自检 → 命令可定位技能包：%s｜占位符残留：%s" %
              ("是" if ok_path else "否", "无" if PLACEHOLDER not in probe else "有"))

    print("""
下一步：
  1. 重启 Qoder（或在 Qoder 里执行 /commands 重新加载）。
  2. 对话框输入 / ，应能看到 qiuzhi、zhaogang、mianshi、jianli、gongsi、rijihua、zhoujihua（及英文别名）。
  3. 先跑 /qiuzhi 看总览。
你的数据会存在：%s""" % os.path.join(targets[0], "skills", SKILL_NAME, "data"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
