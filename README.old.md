# 飞书产品知识库离线检索 Skill

基于飞书知识库的智能离线检索系统，支持向量检索、关键词检索和混合检索。

## 功能特性

### 🎯 核心优势
- **🚀 零配置数据库** - 无需安装独立数据库服务，pip 安装即可使用
- **💾 完全离线运行** - 检索无需联网，数据本地存储
- **🧠 智能混合检索** - 语义 + 关键词，最佳检索效果
- **⚡️ 增量同步** - 只更新变化的文档，节省时间

### 1. 数据采集
- ✅ 通过飞书 Open API 批量下载知识库文档
- ✅ 支持多种文档格式（Doc、Docx、Wiki）
- ✅ 保留文档层级结构和元数据
- ✅ 增量同步更新

### 2. 离线索引
- ✅ 使用 ChromaDB 构建向量索引（**嵌入式数据库，无需单独安装**）
- ✅ 本地 Embedding 模型（sentence-transformers）
- ✅ BM25 关键词索引
- ✅ 文档分块策略优化

### 3. 智能检索
- ✅ 向量语义检索
- ✅ BM25 关键词检索
- ✅ 混合检索（RRF 融合）⭐ 推荐
- ✅ 上下文窗口优化

### 4. OpenClaw 集成
- ✅ 标准 Skill 接口
- ✅ 命令行友好
- ✅ 结构化输出

## 快速开始

### ⚡️ 三步安装（无需数据库）

```bash
# 1. 进入项目目录
cd "Feishu PKB"

# 2. 安装依赖（包含嵌入式 ChromaDB 数据库）
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 填入飞书应用凭证

# 完成！无需安装其他数据库服务
```

> **💡 重要说明**：本方案使用 ChromaDB **嵌入式数据库**，类似 SQLite，通过 pip 安装即可使用，**无需单独安装和配置数据库服务器**。详见 [INSTALLATION.md](INSTALLATION.md)

### 配置飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 开启以下权限：
   - `wiki:wiki:readonly` - 知识库读取
   - `docx:document:readonly` - 文档读取
4. 获取 `App ID` 和 `App Secret`

### 使用流程

#### 步骤 1: 构建索引

```bash
# 首次全量索引
python src/main.py index --full

# 增量更新
python src/main.py sync
```

#### 步骤 2: 检索查询

```bash
# 基本检索
python src/main.py search "如何使用产品功能"

# 指定返回数量
python src/main.py search "API文档" --top-k=10

# 选择检索模式
python src/main.py search "技术架构" --mode=vector  # 向量检索
python src/main.py search "技术架构" --mode=keyword # 关键词检索
python src/main.py search "技术架构" --mode=hybrid  # 混合检索（推荐）
```

#### 步骤 3: 查看文档

```bash
# 查看文档详情
python src/main.py view <doc-id>

# 查看知识库统计
python src/main.py stats
```

## 在 OpenClaw 中使用

```bash
# 加载 Skill
/skill load feishu-pkb-retrieval

# 检索示例
/feishu-pkb search "产品使用指南"

# 同步知识库
/feishu-pkb sync
```

## 架构设计

### 数据流程

```
飞书知识库 (API)
    ↓
文档采集器 (Crawler)
    ↓
文档处理器 (Processor)
    ├── 文本分块 (Chunker)
    └── 元数据提取
    ↓
索引构建器 (Builder)
    ├── 向量索引 (ChromaDB)
    └── 关键词索引 (BM25)
    ↓
检索引擎 (Retriever)
    ├── 向量检索
    ├── 关键词检索
    └── 混合检索 (RRF)
    ↓
结果输出
```

### 技术栈

- **飞书 API**: lark-oapi (官方 SDK)
- **向量数据库**: ChromaDB (离线)
- **Embedding**: sentence-transformers (本地模型)
- **关键词检索**: rank-bm25
- **文档处理**: beautifulsoup4, markdown

## 高级配置

### 自定义分块策略

编辑 `config/config.yaml`:

```yaml
chunking:
  strategy: recursive  # fixed, recursive, semantic
  chunk_size: 512      # 块大小
  chunk_overlap: 50    # 重叠大小
  separators: ["\n\n", "\n", "。", "！", "？"]
```

### 自定义检索权重

```yaml
retrieval:
  vector_weight: 0.6    # 向量检索权重
  keyword_weight: 0.4   # 关键词检索权重
  rerank: true          # 启用重排序
```

## 性能优化

### 索引构建优化
- 批量处理文档
- 并行 Embedding 计算
- 增量更新策略

### 检索优化
- 缓存热门查询
- 预计算文档向量
- 异步加载

## 故障排查

### 常见问题

**Q: 无法连接飞书 API**
```bash
# 检查网络和凭证
python src/utils/check_feishu.py
```

**Q: 索引构建失败**
```bash
# 清空缓存重建
rm -rf data/chromadb
python src/main.py index --full --force
```

**Q: 检索结果不准确**
```bash
# 调整检索参数
python src/main.py search "query" --top-k=20 --threshold=0.6
```

## 路线图

- [ ] 支持图片、表格内容检索
- [ ] 多语言支持
- [ ] 实时问答（RAG）
- [ ] 知识图谱构建
- [ ] Web UI 界面

## 许可证

MIT License
