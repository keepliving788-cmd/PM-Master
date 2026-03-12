#!/bin/bash
# 检查下载进度

PROGRESS_FILE="data/raw/download_progress.json"

if [ ! -f "$PROGRESS_FILE" ]; then
    echo "❌ 进度文件不存在"
    echo "   可能还未开始或刚刚开始"
    exit 1
fi

echo "📊 下载进度"
echo "============================================================"

# 提取进度信息
SUCCESS=$(cat "$PROGRESS_FILE" | grep -o '"success": [0-9]*' | grep -o '[0-9]*')
FAILED=$(cat "$PROGRESS_FILE" | grep -o '"failed": [0-9]*' | grep -o '[0-9]*')
TOTAL=$(cat "$PROGRESS_FILE" | grep -o '"total": [0-9]*' | grep -o '[0-9]*')

if [ -z "$SUCCESS" ]; then SUCCESS=0; fi
if [ -z "$FAILED" ]; then FAILED=0; fi
if [ -z "$TOTAL" ]; then TOTAL=1597; fi

PERCENT=$((SUCCESS * 100 / TOTAL))
REMAINING=$((TOTAL - SUCCESS - FAILED))

echo "  成功: $SUCCESS / $TOTAL ($PERCENT%)"
echo "  失败: $FAILED"
echo "  剩余: $REMAINING"

# 进度条
BAR_LENGTH=50
FILLED=$((SUCCESS * BAR_LENGTH / TOTAL))
BAR=$(printf '%*s' $FILLED | tr ' ' '█')
EMPTY=$(printf '%*s' $((BAR_LENGTH - FILLED)) | tr ' ' '░')
echo "  进度: [$BAR$EMPTY] $PERCENT%"

echo ""

# 预估剩余时间（假设每个文档0.5秒）
REMAINING_SECONDS=$((REMAINING / 2))
REMAINING_MINUTES=$((REMAINING_SECONDS / 60))
echo "  预计剩余: ~$REMAINING_MINUTES 分钟"

echo "============================================================"

# 显示最后几行输出
echo ""
echo "最近下载的文档:"
tail -5 /private/tmp/claude-501/-Users-macuser-Desktop-Start-Skills-Feishu-PKB/tasks/bhooi60o3.output 2>/dev/null | grep "^\[" || echo "  （日志文件未找到）"
