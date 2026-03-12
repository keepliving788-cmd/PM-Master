# 更新日志

## [1.3.0] - 2026-03-12

### ✨ 新增功能

#### 增量学习单个文档 🎉

支持快速学习单个飞书文档，无需重建整个知识库索引！

**新增命令：**
```bash
/feishu-kb learn <文档URL或ID>
```

**功能特点：**
- ⚡ 快速添加：几秒钟即可学习新文档
- 🔄 增量更新：不影响现有知识库内容
- 📝 支持 URL 和文档 ID 两种方式
- 🤖 自动索引：自动更新向量、BM25、SQLite 数据库
- ✅ 即时生效：学习完成后立即可搜索

**使用示例：**
```bash
# 通过 URL 学习
/feishu-kb learn https://xxx.feishu.cn/docx/xxxxx

# 通过文档 ID 学习
/feishu-kb learn doxcnxxxxxx

# 学习后立即搜索
/feishu-kb search 新内容
```

**新增文件：**
- `learn_document.py` - 获取单个飞书文档
- `incremental_index.py` - 增量更新索引
- `INCREMENTAL_LEARNING_GUIDE.md` - 详细使用指南

### 📚 文档更新

- 更新 `skill.json` 添加 `learn` 命令
- 更新 `SKILL.md` 添加增量学习说明
- 新增 `INCREMENTAL_LEARNING_GUIDE.md` 完整指南

---

## [1.2.0] - 2026-03-08

### ✨ 新增功能
- 图片内容理解功能
- 支持检测并标注文档中的图片

### 📊 数据统计
- 文档块数：7507+
- 图片数量：14580+
- 覆盖内容：3.1M+ 字符

---

## [1.1.0] - 2026-03-07

### ✨ 新增功能
- 全量知识库构建
- 海外业务文档支持
- 离线索引优化

---

## [1.0.0] - 2026-03-06

### 🎉 首次发布

**核心功能：**
- 飞书知识库检索
- TF-IDF 向量搜索
- BM25 关键词搜索
- 混合检索模式（RRF 融合）
- OpenClaw Skill 支持

**技术栈：**
- Python 3.8+
- scikit-learn (TF-IDF)
- rank-bm25 (关键词搜索)
- jieba (中文分词)
- SQLite (数据存储)
- lark-oapi (飞书 API)
