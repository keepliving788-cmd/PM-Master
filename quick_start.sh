#!/bin/bash
# 快速启动脚本 - 高精度检索系统

set -e
cd "$(dirname "$0")"

echo "🚀 高精度检索系统 - 快速启动"
echo "=================================="
echo ""

# 步骤1: 检查依赖
echo "📦 步骤1/4: 检查依赖..."
if python3 -c "import lark_oapi, sentence_transformers, jieba" 2>/dev/null; then
    echo "   ✅ 依赖已安装"
else
    echo "   ⚠️  正在安装依赖（约3分钟）..."
    pip3 install -q -r requirements.txt
    echo "   ✅ 依赖安装完成"
fi
echo ""

# 步骤2: 检查配置
echo "📝 步骤2/4: 检查配置..."
if [ -f ".env" ]; then
    echo "   ✅ 配置文件存在"
    # 检查是否有APP_ID
    if grep -q "FEISHU_APP_ID=cli_" .env; then
        echo "   ✅ 飞书凭证已配置"
    else
        echo "   ⚠️  请在 .env 中配置 FEISHU_APP_ID 和 FEISHU_APP_SECRET"
        exit 1
    fi
else
    echo "   ❌ 配置文件不存在"
    exit 1
fi
echo ""

# 步骤3: 测试连接
echo "🔌 步骤3/4: 测试飞书连接..."
if python3 test_api_access.py 2>&1 | grep -q "测试通过"; then
    echo "   ✅ 飞书连接成功"
else
    echo "   ⚠️  飞书连接测试失败，请检查凭证和权限"
    echo "   提示: 运行 'python3 test_api_access.py' 查看详细信息"
fi
echo ""

# 步骤4: 检查索引
echo "📚 步骤4/4: 检查索引状态..."
if [ -d "data/chromadb" ] && [ "$(ls -A data/chromadb 2>/dev/null)" ]; then
    echo "   ✅ 索引已存在"
    echo ""
    echo "=================================="
    echo "✅ 系统已就绪！"
    echo "=================================="
    echo ""
    echo "💡 快速测试:"
    echo "   python3 src/main.py search \"扫码王有哪些型号\" --mode=hybrid"
    echo ""
    echo "📊 查看统计:"
    echo "   python3 src/main.py stats"
    echo ""
else
    echo "   ⚠️  索引尚未构建"
    echo ""
    echo "=================================="
    echo "📋 下一步: 构建索引"
    echo "=================================="
    echo ""
    echo "运行以下命令构建索引（约5-15分钟）:"
    echo "   python3 src/main.py index --full"
    echo ""
    echo "构建完成后即可开始检索:"
    echo "   python3 src/main.py search \"你的查询\" --mode=hybrid"
    echo ""
fi

echo "📖 文档:"
echo "   - 快速上手: cat QUICKSTART_V2.md"
echo "   - 升级说明: cat WHATS_NEW.md"
echo ""
