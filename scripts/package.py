#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把整个技能包打成可分发的 zip。

用法:
    python3 scripts/package.py                      # 输出到 ./dist/
    python3 scripts/package.py --out ~/桌面           # 指定输出目录
    python3 scripts/package.py --name 求职台-v3.1     # 指定包名

规则:
    - 排除 data/（个人岗位与简历数据）、__pycache__、.git、.DS_Store、.pyc
    - 打包前先跑 --check 式校验（缺关键文件直接失败）
    - 生成 SHA256SUMS 与文件清单，便于对方核对
"""
import argparse
import hashlib
import os
import sys
import zipfile
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EXCLUDE_DIRS = {"data", "__pycache__", ".git", "node_modules", ".idea", ".vscode", "dist", "docs"}
EXCLUDE_EXT = {".pyc", ".pyo", ".log", ".bak", ".DS_Store", ".swp"}
MUST_HAVE = ["SKILL.md", "README.md", "VERSION", "LICENSE",
             os.path.join("scripts", "install.py"),
             os.path.join("scripts", "qiuzhi.py"),
             os.path.join("scripts", "plan.py"),
             os.path.join("commands", "qiuzhi.md")]


def collect():
    files = []
    for root, dirs, fs in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in fs:
            if f.endswith(tuple(EXCLUDE_EXT)):
                continue
            p = os.path.join(root, f)
            files.append(os.path.relpath(p, ROOT))
    return sorted(files)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist"))
    ap.add_argument("--name", default="")
    args = ap.parse_args()

    missing = [m for m in MUST_HAVE if not os.path.exists(os.path.join(ROOT, m))]
    if missing:
        print("[ERR] 缺关键文件，先补齐再打包：")
        for m in missing:
            print("  - " + m)
        return 2

    version = open(os.path.join(ROOT, "VERSION"), encoding="utf-8").read().strip()
    name = args.name or ("求职台-qiuzhi-taibao-v" + version)
    os.makedirs(args.out, exist_ok=True)
    outzip = os.path.join(os.path.abspath(args.out), name + ".zip")

    files = collect()
    total = sum(os.path.getsize(os.path.join(ROOT, f)) for f in files)

    # SHA256SUMS / 文件清单
    sums = []
    for f in files:
        sums.append("%s  %s" % (sha256(os.path.join(ROOT, f)), f.replace(os.sep, "/")))
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    manifest = "求职台 v%s ｜ 打包于 %s ｜ 共 %d 个文件\n\n%s\n" % (version, stamp, len(files), "\n".join(sums))

    with zipfile.ZipFile(outzip, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(os.path.join(ROOT, f), os.path.join(name, f).replace(os.sep, "/"))
        z.writestr(os.path.join(name, "SHA256SUMS.txt").replace(os.sep, "/"), manifest)

    print("[OK] %s" % outzip)
    print("     文件 %d 个｜原始 %.1f KB｜压缩后 %.1f KB" % (len(files), total / 1024, os.path.getsize(outzip) / 1024))
    bad = [f for f in files if f.startswith("data" + os.sep)]
    print("     个人数据文件: %s" % ("无" if not bad else "!! 混入 %d 个" % len(bad)))
    print("\n发给对方：解压后双击「安装-Windows.bat」（Windows）或 python3 scripts/install.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
