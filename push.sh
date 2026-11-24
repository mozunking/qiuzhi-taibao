#!/usr/bin/env bash
# 用法: bash push.sh <github用户名> [仓库名] [--public]
# 例:   bash push.sh zhangsan qiuzhi-taibao
set -e
USER="${1:?用法: bash push.sh <github用户名> [仓库名]}"
REPO="${2:-qiuzhi-taibao}"
VIS="${3:---public}"
git branch -M main
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/${USER}/${REPO}.git"
echo "→ 目标: https://github.com/${USER}/${REPO}"
echo "→ 如果仓库还不存在，先在 GitHub 网页上新建一个空仓库（不要勾 README / .gitignore / LICENSE）"
git push -u origin main
echo "完成: https://github.com/${USER}/${REPO}"
