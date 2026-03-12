# 📤 GitHub 上传指南

## ✅ 已完成

- ✅ Git 仓库已初始化
- ✅ 所有文件已添加（105个文件）
- ✅ 初始提交已创建
- ✅ 敏感文件（.env, data/）已被正确忽略

---

## 🚀 方式 1：通过 GitHub 网页（推荐）

### 步骤 1：创建 GitHub 仓库

1. 访问：https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `feishu-kb-skill` （或你喜欢的名字）
   - **Description**: `飞书知识库智能检索系统 - OpenClaw Skill with incremental learning`
   - **Public/Private**: 选择你需要的可见性
   - ⚠️ **不要**勾选 "Add a README file"
   - ⚠️ **不要**勾选 "Add .gitignore"
   - ⚠️ **不要**勾选 "Choose a license"（已有文件）
3. 点击 "Create repository"

### 步骤 2：推送代码到 GitHub

创建仓库后，GitHub 会显示命令。在终端执行：

```bash
cd "/Users/macuser/Desktop/Start/Skills/Feishu PKB"

# 添加远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/feishu-kb-skill.git

# 推送代码
git branch -M main
git push -u origin main
```

### 步骤 3：验证

访问你的 GitHub 仓库页面，确认所有文件已上传。

---

## 🚀 方式 2：使用 GitHub CLI（需安装）

### 安装 GitHub CLI

```bash
# macOS
brew install gh

# 或者从官网下载
# https://cli.github.com/
```

### 认证

```bash
gh auth login
```

### 创建仓库并推送

```bash
cd "/Users/macuser/Desktop/Start/Skills/Feishu PKB"

# 创建公开仓库
gh repo create feishu-kb-skill --public --source=. --remote=origin --push

# 或创建私有仓库
gh repo create feishu-kb-skill --private --source=. --remote=origin --push
```

---

## 📋 推荐的仓库设置

### 仓库名称建议

- `feishu-kb-skill`
- `feishu-knowledge-base`
- `feishu-pkb`
- `openclaw-feishu-skill`

### 仓库描述建议

```
飞书知识库智能检索系统 | Feishu Knowledge Base Intelligent Retrieval System

✨ Features: Offline Search, Incremental Learning, OpenClaw Skill Support
🚀 Tech: TF-IDF + BM25 + RRF Fusion, Python 3.8+
📚 7507+ chunks, 14580+ images, 3.1M+ characters
```

### Topics 建议

添加以下 topics（在仓库页面设置）：

```
feishu
lark
knowledge-base
search-engine
information-retrieval
tfidf
bm25
openclaw
skill
python
offline-search
incremental-learning
```

---

## 🔒 安全检查

### 确认敏感信息未被上传

```bash
cd "/Users/macuser/Desktop/Start/Skills/Feishu PKB"

# 检查 .env 文件
git log --all --full-history -- ".env"
# 应该显示：empty（没有记录）

# 检查 data/ 目录
git log --all --full-history -- "data/"
# 应该显示：empty（没有记录）

# 如果发现敏感文件被提交，立即执行：
# git filter-branch --force --index-filter \
#   "git rm --cached --ignore-unmatch .env" \
#   --prune-empty --tag-name-filter cat -- --all
```

---

## 📝 后续步骤

### 1. 添加 GitHub Actions（可选）

创建 `.github/workflows/test.yml` 实现自动测试：

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      - run: pip install -r requirements.txt
      - run: python3 verify_system.py
```

### 2. 设置 GitHub Pages（可选）

如果想展示文档，可以启用 GitHub Pages：

1. 进入仓库 Settings → Pages
2. Source 选择 "main branch"
3. 文档会自动发布到：`https://YOUR_USERNAME.github.io/feishu-kb-skill/`

### 3. 创建 Release（可选）

```bash
# 创建标签
git tag -a v1.3.0 -m "Release v1.3.0 - Incremental Learning"

# 推送标签
git push origin v1.3.0

# 或使用 gh CLI
gh release create v1.3.0 --title "v1.3.0 - Incremental Learning" --notes "
✨ New Features:
- Incremental learning for single documents
- Fast document addition (3-15 seconds)
- Support document URL/ID input

📚 Documentation:
- INCREMENTAL_LEARNING_GUIDE.md
- FULL_UPDATE_WORKFLOW.md
- UPDATE_METHODS_COMPARISON.md
"
```

---

## 📦 分享给其他人

### 安装说明（README.md 中已包含）

其他人可以通过以下方式安装：

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/feishu-kb-skill.git
cd feishu-kb-skill

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填写飞书凭证

# 初始化
python3 setup_skill.py

# 构建知识库
python3 skill_main.py update
```

---

## 🔄 日常开发流程

### 提交更新

```bash
# 查看修改
git status

# 添加文件
git add .

# 提交
git commit -m "feat: add new feature"

# 推送
git push
```

### 提交消息规范（建议）

```bash
# 新功能
git commit -m "feat: add incremental learning"

# 修复 bug
git commit -m "fix: resolve search timeout issue"

# 文档更新
git commit -m "docs: update installation guide"

# 性能优化
git commit -m "perf: optimize vector search"

# 代码重构
git commit -m "refactor: simplify search engine"
```

---

## 📊 仓库统计

当前提交统计：
- **文件数**: 105 个
- **代码行数**: 23,776 行
- **提交数**: 1 个（初始提交）
- **分支**: main

---

## 🎉 完成！

你的项目已准备好上传到 GitHub！

**下一步：**
1. 访问 https://github.com/new 创建仓库
2. 执行推送命令
3. 分享仓库链接给其他人

**仓库链接格式：**
```
https://github.com/YOUR_USERNAME/feishu-kb-skill
```

---

## 💡 提示

- ✅ 敏感信息已被 .gitignore 排除
- ✅ 初始提交已包含完整功能
- ✅ 所有文档已更新到 v1.3.0
- ✅ 可以安全地公开分享

---

**需要帮助？**
- GitHub 文档: https://docs.github.com/
- Git 教程: https://git-scm.com/doc
