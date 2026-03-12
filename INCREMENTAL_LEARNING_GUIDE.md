# 📚 增量学习功能使用指南

## ✨ 新功能概述

现在支持**增量学习单个飞书文档**，无需重建整个知识库索引！

### 功能特点

✅ **快速添加**：只需几秒钟即可学习新文档
✅ **增量更新**：不影响现有知识库内容
✅ **灵活方便**：支持文档URL或文档ID
✅ **自动索引**：自动更新向量、BM25索引和数据库
✅ **即时生效**：学习完成后立即可以搜索到新内容

---

## 🚀 使用方法

### 方式 1：通过 Skill 命令（推荐）

```bash
# 通过文档URL学习
/feishu-kb learn https://xxx.feishu.cn/docx/xxxxx

# 通过文档ID学习
/feishu-kb learn doxcnxxxxxx

# 或者直接运行
python3 skill_main.py learn https://xxx.feishu.cn/docx/xxxxx
```

### 方式 2：分步执行（高级用户）

```bash
# 第1步：获取文档内容
python3 learn_document.py https://xxx.feishu.cn/docx/xxxxx

# 第2步：更新索引
python3 incremental_index.py data/raw/learned/learned_doxcnxxxxx.txt
```

---

## 📖 完整示例

### 示例 1：学习产品白皮书

```bash
# 假设你有一个新的产品白皮书文档
/feishu-kb learn https://sqb.feishu.cn/docx/new_product_whitepaper

# 输出示例：
# 📚 学习飞书文档: https://sqb.feishu.cn/docx/new_product_whitepaper
#
# [1/3] 获取文档内容...
# 📄 获取文档: new_product_whitepaper (类型: docx)
#    ✅ 成功获取 docx 文档 (15000 字符)
# ✅ 文档获取成功
#
# [2/3] 更新索引...
# 📂 加载现有索引...
#    ✅ 向量: (7507, 768)
#    ✅ BM25索引: 7507 文档
#    ✅ 元数据: 7507 块
#    ✅ 数据库连接成功
# 📄 读取文档: data/raw/learned/learned_new_product_whitepaper.txt
#    ✅ 15000 字符
# ✂️  文档分块...
#    ✅ 生成 12 个块
# 📦 加载Embedding模型...
#    ✅ m3e-base 模型
# 🔢 生成向量...
#    ✅ 向量形状: (12, 768)
# 🔄 合并到现有索引...
#    ✅ 向量: (7507, 768) + (12, 768) = (7519, 768)
#    ✅ BM25: 7507 + 12 = 7519 文档
#    ✅ 数据库: 添加 12 条记录
# 💾 保存索引...
#    ✅ 向量
#    ✅ BM25
#    ✅ 数据库
#    ✅ 元数据
# ✅ 索引更新成功
#
# [3/3] 重新加载搜索引擎...
# ✅ 搜索引擎已重新加载
#
# ✅ 文档学习完成
```

### 示例 2：学习技术方案文档

```bash
# 通过文档ID学习
/feishu-kb learn doxcnABCDEFG123456

# 学习完成后立即测试搜索
/feishu-kb search 新技术方案
```

### 示例 3：批量学习多个文档

```bash
# 可以连续学习多个文档
/feishu-kb learn https://xxx.feishu.cn/docx/doc1
/feishu-kb learn https://xxx.feishu.cn/docx/doc2
/feishu-kb learn https://xxx.feishu.cn/docx/doc3

# 查看更新后的状态
/feishu-kb status
```

---

## 🔍 支持的文档格式

### URL 格式

```bash
# 标准飞书文档 URL
https://xxx.feishu.cn/docx/xxxxx
https://xxx.feishu.cn/docs/xxxxx
https://xxx.feishu.cn/wiki/xxxxx

# 自定义域名
https://sqb.feishu.cn/docx/xxxxx
```

### 文档 ID 格式

```bash
# docx 文档 ID
doxcnxxxxxx

# wiki 文档 ID
wikixxxxxe

# 其他格式的文档 ID
xxxxx-xxxxx-xxxxx
```

---

## 📊 对比：增量学习 vs 全量更新

| 特性 | 增量学习 (`learn`) | 全量更新 (`update`) |
|------|-------------------|-------------------|
| **速度** | ⚡ 快（几秒到十几秒） | 🐌 慢（几分钟） |
| **影响范围** | 仅添加新文档 | 重建所有索引 |
| **使用场景** | 添加单个/少量文档 | 同步整个知识库 |
| **数据来源** | 指定的文档 URL/ID | 配置的知识库空间 |
| **索引更新** | 增量追加 | 完全重建 |

---

## 🎯 最佳实践

### 何时使用 `learn`（增量学习）

✅ 有新产品文档需要添加
✅ 更新了某个文档，想快速同步
✅ 团队成员分享了重要文档
✅ 需要快速测试文档是否可搜索

### 何时使用 `update`（全量更新）

✅ 知识库结构发生重大变化
✅ 定期同步整个知识库（如每周一次）
✅ 初次部署知识库
✅ 索引文件损坏需要重建

### 推荐工作流

```bash
# 1. 初始部署：全量更新
/feishu-kb update

# 2. 日常使用：增量学习
/feishu-kb learn <新文档URL>

# 3. 定期同步：全量更新（每周/每月）
/feishu-kb update

# 4. 随时检查状态
/feishu-kb status
```

---

## 🛠️ 技术实现

### 增量索引流程

```
用户输入文档URL/ID
    ↓
[1] learn_document.py
    - 解析URL提取文档ID
    - 调用飞书API获取文档内容
    - 保存到 data/raw/learned/
    ↓
[2] incremental_index.py
    - 加载现有索引
    - 对新文档分块
    - 生成向量
    - 合并到现有索引
    - 更新 vectors.npz
    - 更新 bm25_index.pkl
    - 更新 kb_data.db
    - 更新 metadata.json
    ↓
[3] 重新加载搜索引擎
    - SimpleSearchEngine 重新初始化
    - 新内容立即可搜索
```

### 文件结构

```
data/
├── raw/
│   ├── wiki_content.txt          # 全量更新的内容
│   └── learned/                  # 增量学习的文档
│       ├── learned_doxcnAAA.txt
│       ├── learned_doxcnBBB.txt
│       └── ...
├── vectors.npz                   # 向量索引（增量追加）
├── bm25_index.pkl               # BM25索引（增量追加）
├── kb_data.db                   # SQLite数据库（增量插入）
└── metadata.json                # 元数据（记录更新次数）
```

---

## 🐛 故障排查

### 问题 1：无法获取文档内容

**错误信息：**
```
❌ 获取文档失败: 无法获取文档内容，请检查文档ID/URL是否正确
```

**解决方案：**
1. 检查文档 URL 是否正确
2. 确认飞书应用是否有访问该文档的权限
3. 检查 `.env` 中的凭证是否正确：
   ```bash
   cat .env | grep FEISHU_APP
   ```

### 问题 2：索引更新失败

**错误信息：**
```
❌ 更新索引失败: ...
```

**解决方案：**
1. 检查 `data/` 目录权限
2. 确认现有索引文件完整性：
   ```bash
   /feishu-kb status
   ```
3. 如果索引损坏，重新全量更新：
   ```bash
   /feishu-kb update
   ```

### 问题 3：学习后搜索不到

**可能原因：**
- 文档内容与查询关键词不匹配
- 需要等待几秒让索引完全生效

**解决方案：**
1. 查看状态确认文档已添加：
   ```bash
   /feishu-kb status
   # 检查 chunk_count 是否增加
   ```

2. 尝试不同的搜索关键词：
   ```bash
   /feishu-kb search <文档中的确切词语>
   ```

3. 使用不同的搜索模式：
   ```bash
   /feishu-kb search <查询> --mode keyword
   ```

---

## 📈 性能指标

| 操作 | 耗时 | 说明 |
|------|------|------|
| **获取文档** | 1-3秒 | 取决于文档大小和网络 |
| **分块处理** | <1秒 | 本地处理 |
| **生成向量** | 1-5秒 | 取决于文档大小和模型 |
| **更新索引** | 1-3秒 | 增量追加 |
| **总耗时** | 3-12秒 | 远快于全量更新 |

---

## 💡 高级用法

### 集成到自动化流程

```bash
#!/bin/bash
# auto_learn.sh - 自动学习多个文档

DOCS=(
    "https://xxx.feishu.cn/docx/doc1"
    "https://xxx.feishu.cn/docx/doc2"
    "https://xxx.feishu.cn/docx/doc3"
)

for doc in "${DOCS[@]}"; do
    echo "学习文档: $doc"
    python3 skill_main.py learn "$doc"

    if [ $? -eq 0 ]; then
        echo "✅ 成功"
    else
        echo "❌ 失败"
    fi
    echo "---"
done

echo "全部完成！"
/feishu-kb status
```

### 通过 Python API 调用

```python
from skill_main import FeishuKBSkill

# 初始化
skill = FeishuKBSkill()

# 学习文档
result = skill.learn("https://xxx.feishu.cn/docx/xxxxx")

if result.get('success'):
    print(f"✅ 学习成功: {result['doc_path']}")

    # 立即搜索验证
    search_result = skill.search("新产品", top_k=3)
    print(f"找到 {search_result['count']} 个结果")
else:
    print(f"❌ 学习失败: {result.get('error')}")
```

---

## 🎉 总结

增量学习功能让知识库更新变得：

✨ **更快** - 几秒钟完成，无需等待
✨ **更灵活** - 想学什么就学什么
✨ **更方便** - 一条命令搞定
✨ **更可靠** - 不影响现有数据

现在就试试吧：

```bash
/feishu-kb learn <你的文档URL>
```

---

## 📚 相关文档

- [README.md](README.md) - 项目主文档
- [OPENCLAW_SKILL_GUIDE.md](OPENCLAW_SKILL_GUIDE.md) - Skill 部署指南
- [SKILL.md](SKILL.md) - Skill 使用说明

---

**有问题？** 查看 [故障排查](#-故障排查) 部分或提交 Issue。
