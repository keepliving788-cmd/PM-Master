# 架构设计文档

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        OpenClaw CLI                          │
│                    (Skill Interface)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      Main Entry (main.py)                    │
│  Commands: index | sync | search | view | stats             │
└──────┬──────────────────────────────────────┬───────────────┘
       │                                       │
       ▼                                       ▼
┌──────────────────┐                  ┌──────────────────────┐
│  Index Manager   │                  │   Search Engine      │
│                  │                  │                      │
│ • build_full     │                  │ • vector_search      │
│ • incremental    │                  │ • keyword_search     │
│ • sync           │                  │ • hybrid_search      │
└────┬─────────────┘                  └──────┬───────────────┘
     │                                       │
     ▼                                       ▼
┌──────────────────┐                  ┌──────────────────────┐
│ Feishu Client    │                  │   Retrievers         │
│                  │                  │                      │
│ • list_nodes     │                  │ • VectorSearch       │
│ • get_content    │                  │ • KeywordSearch      │
│ • traverse       │                  │ • HybridSearch       │
└────┬─────────────┘                  └──────────────────────┘
     │
     ▼
┌──────────────────┐
│ Doc Processor    │
│                  │
│ • clean_content  │
│ • chunk_text     │
└────┬─────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│                        Storage Layer                         │
│                                                              │
│  ┌─────────────────┐              ┌─────────────────────┐  │
│  │  Vector Store   │              │   Document Store    │  │
│  │   (ChromaDB)    │              │   (JSON Files)      │  │
│  └─────────────────┘              └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
     │                                       │
     ▼                                       ▼
┌─────────────────┐              ┌─────────────────────────┐
│  data/chromadb  │              │   data/processed/       │
│  • embeddings   │              │   • doc_id.json         │
│  • metadata     │              │   • index.json          │
└─────────────────┘              └─────────────────────────┘
```

## 核心模块

### 1. Indexer (索引构建模块)

#### FeishuClient
**职责：** 与飞书 API 交互
```python
class FeishuClient:
    - list_wiki_nodes()        # 获取节点列表
    - get_wiki_node_info()     # 获取节点信息
    - get_document_content()   # 获取文档内容
    - traverse_wiki_space()    # 遍历知识空间
```

**API 调用流程：**
```
1. 获取 Access Token (自动)
2. 列出知识空间节点
3. 遍历节点树（递归）
4. 获取文档内容（批量）
5. 错误重试机制
```

#### DocProcessor
**职责：** 文档处理和分块
```python
class DocumentProcessor:
    - process_document()    # 处理文档
    - _clean_content()      # 清洗内容
    - _chunk_text()         # 文本分块
    - _chunk_recursive()    # 递归分块（推荐）
    - _chunk_semantic()     # 语义分块（TODO）
```

**分块策略：**
- **Fixed**: 固定大小分块
- **Recursive**: 按分隔符递归分块 ⭐
- **Semantic**: 语义边界分块（计划中）

#### IndexManager
**职责：** 索引构建管理
```python
class IndexManager:
    - build_full_index()        # 全量索引
    - build_incremental_index() # 增量索引
    - sync()                    # 同步
```

**索引构建流程：**
```
1. 遍历飞书知识空间
2. 获取文档内容
3. 文档处理和分块
4. 计算 Embeddings
5. 存储到 VectorStore
6. 保存文档元数据
7. 持久化索引
```

### 2. Retriever (检索模块)

#### SearchEngine
**职责：** 统一检索接口
```python
class SearchEngine:
    - search()            # 统一检索入口
    - get_document()      # 获取文档
    - get_stats()         # 统计信息
```

#### VectorSearch
**职责：** 向量语义检索
```python
class VectorSearch:
    - search()    # 向量检索
```

**检索原理：**
```
1. 查询文本 → Embedding
2. 向量相似度计算 (Cosine)
3. 返回 Top-K 结果
```

#### KeywordSearch
**职责：** 关键词检索
```python
class KeywordSearch:
    - search()             # BM25 检索
    - _build_bm25_index()  # 构建索引
```

**BM25 算法：**
```
score(D,Q) = Σ IDF(qi) × f(qi,D) × (k1 + 1)
                        ─────────────────────────
                        f(qi,D) + k1 × (1-b + b×|D|/avgdl)

- D: 文档
- Q: 查询
- qi: 查询词
- f(qi,D): 词频
- k1, b: 参数
```

#### HybridSearch
**职责：** 混合检索
```python
class HybridSearch:
    - search()          # 混合检索
    - _rrf_fusion()     # RRF 融合 ⭐
    - _linear_fusion()  # 线性融合
```

**RRF (Reciprocal Rank Fusion):**
```
score(d) = Σ    α
            ─────────
            k + rank(d)

- d: 文档
- rank(d): 文档在列表中的排名
- k: 常数 (默认 60)
- α: 权重
```

### 3. Storage (存储模块)

#### VectorStore
**职责：** 向量存储（ChromaDB）
```python
class VectorStore:
    - add_documents()     # 添加文档
    - query()             # 查询
    - delete_document()   # 删除文档
    - clear()             # 清空
```

**ChromaDB 特点：**
- 完全本地运行
- 自动持久化
- 支持元数据过滤
- HNSW 索引（高性能）

#### DocumentStore
**职责：** 文档存储（JSON）
```python
class DocumentStore:
    - save_document()     # 保存文档
    - get_document()      # 获取文档
    - list_documents()    # 列出文档
    - delete_document()   # 删除文档
```

**存储结构：**
```
data/processed/
├── index.json          # 文档索引
├── doc_id_1.json       # 文档 1
├── doc_id_2.json       # 文档 2
└── ...
```

## 数据流

### 索引构建流程

```
飞书 API
   │
   ▼
[FeishuClient.get_document_content()]
   │
   ▼
Raw Document
   │
   ▼
[DocProcessor.process_document()]
   │ • 清洗 HTML
   │ • 分块文本
   ▼
Processed Document + Chunks
   │
   ├─► [VectorStore.add_documents()]
   │      │ • 计算 Embeddings
   │      │ • 存储向量
   │      ▼
   │   ChromaDB
   │
   └─► [DocumentStore.save_document()]
          │ • 保存 JSON
          ▼
       JSON Files
```

### 检索流程

```
User Query
   │
   ▼
[SearchEngine.search()]
   │
   ├─► mode=vector ──► [VectorSearch.search()]
   │                      │ • Query Embedding
   │                      │ • Cosine Similarity
   │                      ▼
   │                   ChromaDB Results
   │
   ├─► mode=keyword ─► [KeywordSearch.search()]
   │                      │ • BM25 Scoring
   │                      ▼
   │                   BM25 Results
   │
   └─► mode=hybrid ──► [HybridSearch.search()]
                          │ • Vector + Keyword
                          │ • RRF Fusion
                          ▼
                       Fused Results
   │
   ▼
[Enrich with metadata]
   │
   ▼
Final Results
```

## 配置系统

### 配置文件层次

```
config/config.yaml       # 主配置文件
   ↓
.env                     # 环境变量
   ↓
Runtime Config          # 运行时配置
```

### 配置加载流程

```python
1. 加载 config.yaml
2. 加载 .env 环境变量
3. 替换 ${VAR} 占位符
4. 创建 Config 对象
5. 传递给各模块
```

## 扩展性设计

### 1. 新增检索模式

```python
# 1. 创建新的检索器
class SemanticSearch:
    def search(self, query, top_k):
        # 实现语义检索
        pass

# 2. 在 SearchEngine 中注册
self.semantic_search = SemanticSearch(config)

# 3. 添加到 search() 方法
if mode == 'semantic':
    return self.semantic_search.search(query, top_k)
```

### 2. 新增文档类型

```python
# 在 FeishuClient 中添加
def _get_sheet_content(self, sheet_token):
    # 实现表格文档获取
    pass
```

### 3. 新增存储后端

```python
# 实现新的 Store
class PostgreSQLStore:
    def save_document(self, doc):
        # 保存到 PostgreSQL
        pass
```

## 性能优化

### 1. 索引构建优化

- **并行处理**: 多线程下载文档
- **批量 Embedding**: 批量计算向量
- **增量更新**: 只处理变化的文档

### 2. 检索优化

- **缓存**: LRU 缓存热门查询
- **索引优化**: HNSW 加速向量检索
- **预计算**: 预先计算文档统计信息

### 3. 内存优化

- **流式处理**: 大文件流式读取
- **按需加载**: 懒加载文档内容
- **定期清理**: GC 触发阈值

## 安全考虑

### 1. API 安全

- App Secret 环境变量存储
- 不记录敏感信息到日志
- Token 自动刷新机制

### 2. 数据安全

- 本地存储，不上传到云端
- 支持数据加密（可选）
- 访问控制（文件权限）

## 监控与日志

### 日志级别

```python
DEBUG   - 详细调试信息
INFO    - 一般信息
WARNING - 警告信息
ERROR   - 错误信息
```

### 关键指标

- 索引构建时间
- 检索响应时间
- 文档数量和大小
- 内存使用情况

---

**版本**: 1.0.0
**最后更新**: 2026-03-06
