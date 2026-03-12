# 飞书离线知识库系统使用指南

## 📋 系统概述

这是一个基于飞书知识库的离线检索系统，支持：
- ✅ 自动从飞书知识库获取内容
- ✅ 智能分块与向量化索引
- ✅ 混合检索（TF-IDF向量 + BM25关键词）
- ✅ 飞书机器人对话接口
- ✅ 完全离线运行（构建后）

## 🚀 快速开始

### 1. 首次构建离线知识库

```bash
# 步骤1: 从飞书获取知识库内容
python3 fetch_wiki_content.py

# 步骤2: 构建离线索引
python3 build_offline_kb_fast.py

# 步骤3: 测试搜索功能
python3 test_simple_search.py
```

### 2. 启动飞书机器人服务

```bash
# 启动后端服务
python3 bot_server.py
```

服务将监听在 `http://0.0.0.0:8080`

### 3. 测试接口

```bash
# 健康检查
curl http://localhost:8080/health

# 测试搜索
curl -X POST http://localhost:8080/test \
  -H "Content-Type: application/json" \
  -d '{"query":"扫码王"}'
```

## 📁 文件说明

### 核心脚本

- `fetch_wiki_content.py` - 从飞书获取知识库内容
- `build_offline_kb_fast.py` - 构建离线索引（快速版，使用TF-IDF）
- `bot_server.py` - 飞书机器人后端服务
- `test_simple_search.py` - 测试搜索功能

### 数据文件

```
data/
├── raw/
│   └── wiki_content.txt       # 原始知识库内容
├── vectors.npz                # TF-IDF向量
├── bm25_index.pkl            # BM25索引
├── tfidf_vectorizer.pkl      # TF-IDF向量化器
├── kb_data.db                # SQLite数据库
└── metadata.json             # 元数据
```

### 源码模块

```
src/
├── utils/
│   ├── config.py             # 配置管理
│   ├── smart_chunker.py      # 智能分块
│   └── embedder.py           # 向量化（m3e-base，可选）
└── retriever/
    └── simple_search.py      # 简化版检索引擎
```

## 🔧 配置文件

### .env
```bash
FEISHU_APP_ID=cli_a91379879838dcee
FEISHU_APP_SECRET=你的SECRET
FEISHU_WIKI_SPACE_ID=7480754861085147139
```

### config/config.yaml
检索参数、模型设置等详细配置

## 📊 检索模式

### 1. 向量检索 (vector)
使用TF-IDF向量相似度

```python
results = search_engine.search("扫码王", mode='vector', top_k=5)
```

### 2. 关键词检索 (keyword)
使用BM25算法

```python
results = search_engine.search("扫码王", mode='keyword', top_k=5)
```

### 3. 混合检索 (hybrid) - 推荐
使用RRF融合向量和关键词结果

```python
results = search_engine.search("扫码王", mode='hybrid', top_k=5)
```

## 🤖 飞书机器人配置

### 1. 配置Webhook URL

在飞书开放平台配置事件订阅：
```
http://你的服务器IP:8080/webhook
```

### 2. 启用权限

需要的权限：
- `im:message:receive_v1` - 接收消息
- `im:message` - 发送消息

### 3. 测试机器人

在飞书中@机器人发送消息：
```
@机器人 扫码王有哪些型号
```

机器人会从离线知识库查询并返回结果。

## 🔄 更新知识库

当飞书知识库内容更新后：

```bash
# 重新获取内容
python3 fetch_wiki_content.py

# 重新构建索引
python3 build_offline_kb_fast.py

# 重启服务（会自动加载新索引）
pkill -f bot_server.py
python3 bot_server.py
```

## 📈 性能特点

- **构建速度**: ~10秒（10个文档块）
- **检索延迟**: <100ms
- **内存占用**: ~200MB
- **存储大小**: ~2MB

## 🎯 下一步计划

- [ ] 使用m3e-base替代TF-IDF（需要下载模型）
- [ ] 添加Cross-Encoder reranking
- [ ] 支持增量更新
- [ ] 添加缓存层
- [ ] 支持多知识库

## ❓ 常见问题

### Q: 为什么使用TF-IDF而不是m3e-base？
A: m3e-base模型下载较慢，TF-IDF作为快速备选方案，效果也不错。等网络条件好时可以更新。

### Q: 如何提升检索精度？
A:
1. 使用hybrid模式（已启用）
2. 等m3e-base模型下载完成后重新构建
3. 调整config.yaml中的参数

### Q: 机器人无法回复？
A: 检查：
1. bot_server.py是否正常运行
2. Webhook URL是否正确配置
3. 权限是否正确启用
4. .env文件中的凭证是否有效

## 📞 技术支持

如有问题，请检查：
1. 日志输出（带有loguru格式的彩色日志）
2. data/metadata.json中的构建信息
3. /health接口的状态

---

🎉 **系统已完成构建，可以开始使用！**
