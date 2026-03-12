#!/bin/bash
# 启动飞书机器人服务

echo "========================================"
echo "  飞书离线知识库机器人"
echo "========================================"
echo ""

# 检查索引是否存在
if [ ! -f "data/vectors.npz" ]; then
    echo "❌ 未找到索引文件"
    echo ""
    echo "请先构建离线知识库："
    echo "  1. python3 fetch_wiki_content.py"
    echo "  2. python3 build_offline_kb_fast.py"
    echo ""
    exit 1
fi

echo "✅ 索引文件已找到"
echo ""

# 显示索引信息
if [ -f "data/metadata.json" ]; then
    echo "📊 索引信息:"
    cat data/metadata.json
    echo ""
fi

# 检查端口
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口 8080 已被占用"
    echo "   停止旧服务..."
    pkill -f "python3 bot_server.py" 2>/dev/null
    sleep 2
fi

echo "🚀 启动机器人服务..."
echo ""
python3 bot_server.py
