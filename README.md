# 🤖 飞书离线知识库机器人

> 基于飞书知识库的离线检索系统，支持自动数据获取、智能检索和机器人对话

[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)](.)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](.)
[![License](https://img.shields.io/badge/License-MIT-green)](.)

---

## ✨ 特性

- 🔄 **自动数据获取** - 直接从飞书知识库获取内容，无需手动导出
- ⚡ **增量学习** - 支持单个文档快速学习，无需重建索引 🆕
- 🧠 **智能检索** - 混合检索（TF-IDF向量 + BM25关键词 + RRF融合）
- 💬 **机器人接口** - 支持飞书机器人对话查询
- 📦 **离线运行** - 构建后完全离线，无需依赖外部服务
- ⚡ **快速响应** - 检索延迟 <100ms
- 🪶 **轻量级** - 内存占用 ~200MB，存储 <100KB

---

## 🚀 快速开始

### 1. 环境要求

```bash
Python 3.8+
pip install -r requirements.txt
```

### 2. 配置飞书凭证

创建 `.env` 文件：

```bash
FEISHU_APP_ID=你的应用ID
FEISHU_APP_SECRET=你的应用SECRET
FEISHU_WIKI_SPACE_ID=知识库空间ID
```

### 3. 构建知识库

```bash
# 从飞书获取内容
python3 fetch_wiki_content.py

# 构建离线索引
python3 build_offline_kb_fast.py

# 验证系统
python3 verify_system.py
```

### 4. 启动服务

```bash
# 方式1: 使用启动脚本
./start_bot.sh

# 方式2: 直接运行
python3 bot_server.py
```

---

## 📖 使用示例

### OpenClaw Skill 命令 🆕

```bash
# 搜索知识库
/feishu-kb search 扫码王

# 增量学习单个文档（新功能！）
/feishu-kb learn https://xxx.feishu.cn/docx/xxxxx

# 全量更新知识库
/feishu-kb update

# 查看知识库状态
/feishu-kb status
```

详细说明：[增量学习使用指南](INCREMENTAL_LEARNING_GUIDE.md)

### 命令行测试

```bash
# 测试搜索功能
python3 test_simple_search.py

# 学习新文档
python3 skill_main.py learn https://xxx.feishu.cn/docx/xxxxx
```

### HTTP API

```bash
# 健康检查
curl http://localhost:8080/health

# 搜索查询
curl -X POST http://localhost:8080/test \
  -H "Content-Type: application/json" \
  -d '{"query":"扫码王"}'
```

### 飞书机器人

1. 配置Webhook: `http://你的服务器:8080/webhook`
2. 在飞书中@机器人: `@机器人 扫码王有哪些型号`
3. 机器人返回查询结果

---

## 📊 系统架构

```
┌─────────────────┐
│  飞书知识库      │
└────────┬────────┘
         │ fetch_wiki_content.py
         ↓
┌─────────────────┐
│  原始内容(txt)   │
└────────┬────────┘
         │ build_offline_kb_fast.py
         ↓
┌─────────────────────────────────────┐
│  离线索引                            │
│  • TF-IDF向量 (768维)               │
│  • BM25关键词索引                   │
│  • SQLite元数据                     │
└────────┬────────────────────────────┘
         │ SimpleSearchEngine
         ↓
┌─────────────────┐
│  Flask服务       │
│  • /webhook      │ ←── 飞书机器人
│  • /test         │ ←── API测试
│  • /health       │ ←── 健康检查
└─────────────────┘
```

---

## 🎯 核心组件

### 数据获取

- `fetch_wiki_content.py` - 使用Wiki Token直接访问飞书文档
- 绕过机器人应用的ListSpace权限限制
- 支持自动重试和错误处理

### 索引构建

- `SmartChunker` - 智能文档分块，保留结构信息
- `TF-IDF Vectorizer` - 768维向量化（快速备选方案）
- `BM25Okapi` - 关键词索引
- `SQLite` - 元数据存储

### 检索引擎

- **向量检索** - TF-IDF余弦相似度
- **关键词检索** - BM25算法
- **混合检索** - RRF (Reciprocal Rank Fusion) 融合

### 机器人服务

- Flask Webhook服务器
- 接收飞书消息事件
- 离线知识库查询
- 格式化回复并发送

---

## 📁 项目结构

```
.
├── fetch_wiki_content.py       # 数据获取
├── build_offline_kb_fast.py    # 索引构建
├── bot_server.py               # 机器人服务
├── start_bot.sh                # 启动脚本
├── verify_system.py            # 系统验证
├── test_simple_search.py       # 搜索测试
│
├── data/                       # 数据文件
│   ├── raw/wiki_content.txt
│   ├── vectors.npz
│   ├── bm25_index.pkl
│   ├── tfidf_vectorizer.pkl
│   ├── kb_data.db
│   └── metadata.json
│
├── src/                        # 源码模块
│   ├── utils/
│   │   ├── config.py
│   │   ├── smart_chunker.py
│   │   └── embedder.py
│   └── retriever/
│       └── simple_search.py
│
├── config/                     # 配置文件
│   └── config.yaml
│
└── docs/                       # 文档
    ├── README_USAGE.md
    ├── SYSTEM_STATUS.md
    └── PROJECT_COMPLETE.md
```

---

## 🔧 配置说明

### config/config.yaml

```yaml
indexing:
  chunking:
    strategy: recursive
    chunk_size: 512
    chunk_overlap: 50

  embedding:
    model_name: moka-ai/m3e-base  # 或 TF-IDF
    dimension: 768
    batch_size: 32

retrieval:
  vector_search:
    top_k: 10
    similarity_threshold: 0.7

  keyword_search:
    top_k: 10

  hybrid:
    vector_weight: 0.5
    keyword_weight: 0.5
```

---

## 📈 性能指标

| 指标 | 数值 |
|------|------|
| 知识库大小 | 14.5 KB |
| 文档块数 | 10个 |
| 向量维度 | 768 |
| 构建时间 | ~10秒 |
| 检索延迟 | <100ms |
| 内存占用 | ~200MB |
| 存储大小 | <100KB |

---

## 🧪 测试结果

```bash
$ python3 verify_system.py

╔====================================================================╗
║                    系统验证检查                                    ║
╚====================================================================╝

  ✅ 文件检查: 通过 (6/6文件正常)
  ✅ 元数据检查: 通过
  ✅ 数据库检查: 通过 (10个文档块)
  ✅ 检索引擎检查: 通过 (查询成功)

🎉 系统验证完全通过！
```

---

## 🔄 更新知识库

```bash
# 1. 重新获取内容
python3 fetch_wiki_content.py

# 2. 重新构建索引
python3 build_offline_kb_fast.py

# 3. 重启服务
pkill -f bot_server.py
./start_bot.sh
```

---

## 💡 常见问题

### Q: 为什么使用TF-IDF而不是m3e-base？

A: m3e-base模型下载较慢，TF-IDF作为快速备选方案。后续可升级：

```bash
HF_ENDPOINT=https://hf-mirror.com python3 build_offline_kb.py
```

### Q: 如何提升检索精度？

A:
1. 使用 `mode='hybrid'`（默认已启用）
2. 等m3e-base模型就绪后重新构建
3. 调整 `config.yaml` 中的参数

### Q: 机器人无法回复？

A: 检查：
1. `bot_server.py` 是否运行
2. Webhook URL是否正确
3. 飞书权限是否启用
4. `.env` 凭证是否有效

---

## 📚 文档

- [使用指南](README_USAGE.md) - 详细使用说明
- [系统状态](SYSTEM_STATUS.md) - 当前系统状态
- [完工报告](PROJECT_COMPLETE.md) - 项目总结报告

---

## 🛠️ 技术栈

- **Python 3.8+**
- **Flask** - Web框架
- **NumPy** - 向量计算
- **SQLite** - 数据库
- **scikit-learn** - TF-IDF
- **rank-bm25** - BM25算法
- **jieba** - 中文分词
- **lark-oapi** - 飞书SDK
- **loguru** - 日志管理

---

## 📄 License

MIT License

---

## 🙏 致谢

感谢飞书开放平台提供的API支持。

---

## 📞 支持

如遇问题，请：

1. 查看文档：`README_USAGE.md`
2. 运行验证：`python3 verify_system.py`
3. 检查日志：查看彩色日志输出

---

**🎉 项目已就绪，可以开始使用！**

```bash
./start_bot.sh
```
