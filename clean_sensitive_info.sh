#!/bin/bash
# 清理敏感信息脚本

set -e

echo "======================================"
echo "  清理敏感信息"
echo "======================================"
echo

# 需要删除的文件（包含真实凭证）
FILES_TO_DELETE=(
    "当前状态.txt"
    "立即行动.md"
    "SYSTEM_STATUS.md"
    "README_USAGE.md"
)

# 需要替换敏感信息的文件
FILES_TO_SANITIZE=(
    "QUICKSTART_V2.md"
    "FULL_UPDATE_WORKFLOW.md"
)

echo "📋 将删除以下文件（包含真实凭证）："
for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        echo "  ❌ $file"
    fi
done
echo

echo "📝 将清理以下文件中的敏感信息："
for file in "${FILES_TO_SANITIZE[@]}"; do
    if [ -f "$file" ]; then
        echo "  🔧 $file"
    fi
done
echo

read -p "是否继续? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "取消操作"
    exit 0
fi

echo
echo "======================================"
echo "开始清理..."
echo "======================================"
echo

# 删除包含真实凭证的文件
for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        git rm "$file" 2>/dev/null || rm "$file"
        echo "✅ 已删除: $file"
    fi
done

# 替换敏感信息
# APP_ID
echo
echo "替换 APP_ID..."
find . -type f \( -name "*.md" -o -name "*.txt" \) \
    -not -path "./.git/*" \
    -exec sed -i '' 's/cli_a91379879838dcee/cli_xxxxxxxxxxxxxxxxx/g' {} \;

# Space ID
echo "替换 Space ID..."
find . -type f \( -name "*.md" -o -name "*.txt" \) \
    -not -path "./.git/*" \
    -exec sed -i '' 's/7333556703297/xxxxxxxxxx/g' {} \;

echo
echo "======================================"
echo "✅ 清理完成！"
echo "======================================"
echo
echo "已处理的敏感信息："
echo "  - APP_ID: cli_a91379879838dcee → cli_xxxxxxxxxxxxxxxxx"
echo "  - Space ID: 7333556703297 → xxxxxxxxxx"
echo "  - Wiki Token: N9kgwANVwifcisk9UT6cDOFInRe (保留示例)"
echo
echo "下一步："
echo "  1. 检查修改: git status"
echo "  2. 查看差异: git diff"
echo "  3. 提交修改: git add . && git commit -m 'chore: remove sensitive information'"
echo "  4. 推送更新: git push"
echo
