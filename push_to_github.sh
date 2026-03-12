#!/bin/bash
# 推送到 GitHub 的快速脚本

set -e

echo "======================================"
echo "  推送到 GitHub"
echo "======================================"
echo

# 检查是否已配置远程仓库
if git remote | grep -q "origin"; then
    echo "✅ 已配置远程仓库"
    git remote -v
    echo

    read -p "是否推送到现有仓库? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "取消推送"
        exit 0
    fi
else
    echo "⚠️  未配置远程仓库"
    echo
    echo "请先创建 GitHub 仓库，然后输入仓库 URL："
    echo "格式: https://github.com/YOUR_USERNAME/REPO_NAME.git"
    echo
    read -p "仓库 URL: " repo_url

    if [ -z "$repo_url" ]; then
        echo "❌ 未输入仓库 URL"
        exit 1
    fi

    echo
    echo "添加远程仓库..."
    git remote add origin "$repo_url"
    echo "✅ 远程仓库已添加"
fi

echo
echo "======================================"
echo "推送代码到 GitHub..."
echo "======================================"
echo

# 设置主分支
git branch -M main

# 推送
git push -u origin main

echo
echo "======================================"
echo "✅ 推送成功！"
echo "======================================"
echo

# 获取仓库 URL
repo_url=$(git remote get-url origin)
repo_url=${repo_url%.git}
repo_url=${repo_url/git@github.com:/https://github.com/}

echo
echo "🎉 你的项目已上传到 GitHub！"
echo
echo "仓库地址:"
echo "  $repo_url"
echo
echo "下一步:"
echo "  1. 访问仓库页面查看"
echo "  2. 添加 Topics 标签"
echo "  3. 完善仓库描述"
echo "  4. 邀请协作者"
echo

# 尝试打开浏览器
if command -v open &> /dev/null; then
    read -p "是否在浏览器中打开仓库? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "$repo_url"
    fi
fi
