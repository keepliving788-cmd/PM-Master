#!/bin/bash
# 增量学习功能示例脚本

echo "======================================"
echo "  增量学习功能演示"
echo "======================================"
echo

# 示例文档 URL（需要替换为真实的文档URL）
DOC_URL="https://xxx.feishu.cn/docx/your_document_id"

echo "📚 本脚本演示如何使用增量学习功能"
echo
echo "用法："
echo "  ./example_learn.sh <文档URL或ID>"
echo
echo "示例："
echo "  ./example_learn.sh https://xxx.feishu.cn/docx/xxxxx"
echo "  ./example_learn.sh doxcnxxxxxx"
echo

if [ -z "$1" ]; then
    echo "⚠️  请提供文档URL或ID作为参数"
    echo
    echo "例如："
    echo "  ./example_learn.sh https://sqb.feishu.cn/docx/xxxxx"
    exit 1
fi

DOC_URL="$1"

echo "======================================"
echo "步骤 1: 学习文档"
echo "======================================"
echo "文档: $DOC_URL"
echo

python3 skill_main.py learn "$DOC_URL"

if [ $? -eq 0 ]; then
    echo
    echo "======================================"
    echo "步骤 2: 查看更新后的状态"
    echo "======================================"
    echo

    python3 skill_main.py status

    echo
    echo "======================================"
    echo "步骤 3: 测试搜索新内容"
    echo "======================================"
    echo

    read -p "请输入搜索关键词（按回车跳过）: " keyword

    if [ -n "$keyword" ]; then
        echo
        python3 skill_main.py search "$keyword" --top-k 3
    fi

    echo
    echo "======================================"
    echo "✅ 演示完成！"
    echo "======================================"
    echo
    echo "💡 提示："
    echo "  - 使用 /feishu-kb learn <URL> 学习更多文档"
    echo "  - 使用 /feishu-kb search <查询> 搜索知识库"
    echo "  - 使用 /feishu-kb status 查看状态"
    echo
else
    echo
    echo "❌ 学习失败！"
    echo
    echo "故障排查："
    echo "  1. 检查文档URL是否正确"
    echo "  2. 检查飞书应用权限"
    echo "  3. 查看 .env 配置"
    echo
fi
