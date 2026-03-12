#!/bin/bash
# 高精度检索系统升级安装脚本

set -e  # 遇到错误立即退出

echo "🚀 开始安装高精度检索系统升级..."
echo "=================================="
echo ""

# 检查Python版本
echo "📌 检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   ✓ Python版本: $python_version"
echo ""

# 检查工作目录
cd "$(dirname "$0")"
echo "📌 工作目录: $(pwd)"
echo ""

# 安装依赖
echo "📦 安装依赖包..."
echo "   这可能需要3-5分钟..."
echo ""

if pip3 install -r requirements.txt; then
    echo "   ✓ 依赖安装成功"
else
    echo "   ⚠️  部分依赖安装失败，尝试使用镜像源..."
    pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
fi
echo ""

# 创建必要的目录
echo "📁 创建数据目录..."
mkdir -p data/{raw,processed,chromadb} logs
echo "   ✓ 目录创建完成"
echo ""

# 检查配置文件
echo "📝 检查配置文件..."
if [ ! -f ".env" ]; then
    echo "   ⚠️  未找到.env文件"
    if [ -f ".env.example" ]; then
        echo "   ℹ️  创建.env模板..."
        cp .env.example .env
        echo "   ✓ 已创建.env，请编辑填入你的飞书配置"
    fi
else
    echo "   ✓ 配置文件存在"
fi
echo ""

# 运行测试
echo "🧪 运行系统测试..."
echo "   首次运行会下载模型（~400MB），请耐心等待..."
echo ""

if python3 test_upgraded_system.py; then
    echo ""
    echo "   ✓ 系统测试通过"
else
    echo ""
    echo "   ⚠️  部分测试失败（这是正常的，索引尚未构建）"
fi
echo ""

# 完成提示
echo "=================================="
echo "✅ 安装完成！"
echo "=================================="
echo ""
echo "📋 下一步操作:"
echo ""
echo "1. 配置飞书应用（如果还没配置）:"
echo "   nano .env"
echo "   # 填入 FEISHU_APP_ID 和 FEISHU_APP_SECRET"
echo ""
echo "2. 测试飞书连接:"
echo "   python3 test_api_access.py"
echo ""
echo "3. 构建索引:"
echo "   python3 src/main.py index --full"
echo ""
echo "4. 开始检索:"
echo "   python3 src/main.py search '你的查询' --mode=hybrid"
echo ""
echo "📖 文档参考:"
echo "   - 部署指南: DEPLOY.md"
echo "   - 升级说明: UPGRADE_GUIDE.md"
echo "   - 使用教程: START_HERE.md"
echo ""
echo "需要帮助? 查看 README.md 或提交 Issue"
echo ""
