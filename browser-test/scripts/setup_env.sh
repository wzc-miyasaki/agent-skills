#!/bin/bash
# 浏览器测试环境初始化脚本
# 使用 uv 创建虚拟环境并安装 Playwright

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "=== 浏览器测试环境初始化 ==="

# 创建虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    echo "[1/3] 创建 Python 虚拟环境..."
    cd "$SCRIPT_DIR"
    uv venv .venv
else
    echo "[1/3] 虚拟环境已存在，跳过创建"
fi

# 安装依赖
echo "[2/3] 安装 Playwright..."
cd "$SCRIPT_DIR"
uv pip install playwright requests

# 安装浏览器
echo "[3/3] 安装 Chromium 浏览器..."
"$VENV_DIR/bin/playwright" install chromium

echo ""
echo "=== 环境初始化完成 ==="
echo "虚拟环境路径: $VENV_DIR"
echo "Python 路径: $VENV_DIR/bin/python"
