# 文件总览

## 📂 项目结构

```
Feishu PKB/
├── 📖 文档文件 (Markdown)
├── ⚙️ 配置文件 (YAML/Config)
├── 🐍 源代码 (Python)
└── 📦 其他文件
```

---

## 📖 文档文件（按阅读顺序）

### 🌟 首次使用（必读）

| 文件 | 说明 | 用途 |
|------|------|------|
| **START_HERE.md** | 📍 **从这里开始** | 总览和快速导航 |
| **SETUP_GUIDE.md** | 🔧 飞书应用配置指南 | 详细配置步骤 |
| **CHECK_CONFIG.md** | ✅ 配置检查清单 | 测试前检查 |
| **QUICKSTART.md** | ⚡️ 5分钟快速上手 | 快速开始使用 |

### 📚 深入了解

| 文件 | 说明 | 适合 |
|------|------|------|
| **README.md** | 📘 完整功能文档 | 全面了解功能 |
| **ARCHITECTURE.md** | 🏗️ 架构设计文档 | 了解技术架构 |
| **INSTALLATION.md** | 💾 安装说明 | 数据库安装疑问 |
| **DATABASE_COMPARISON.md** | ⚖️ 数据库方案对比 | 技术选型参考 |
| **PROJECT_SUMMARY.md** | 📊 项目总结 | 整体概览 |
| **FILES_OVERVIEW.md** | 📂 本文件 | 文件导航 |

---

## ⚙️ 配置文件

| 文件 | 说明 | 用途 |
|------|------|------|
| **skill.yaml** | Skill 配置 | OpenClaw 集成 |
| **config/config.yaml** | 主配置文件 | 运行时配置 |
| **.env.example** | 环境变量模板 | 配置模板 |
| **.env** | 环境变量（需创建） | 实际配置 |
| **requirements.txt** | Python 依赖 | pip 安装 |
| **Makefile** | Make 命令 | 常用命令 |
| **.gitignore** | Git 忽略规则 | 版本控制 |

---

## 🐍 源代码文件

### 主入口

| 文件 | 说明 |
|------|------|
| **src/main.py** | CLI 主入口，命令行接口 |
| **test_api_access.py** | API 连接测试脚本 |

### 索引构建模块 (src/indexer/)

| 文件 | 说明 |
|------|------|
| **feishu_client.py** | 飞书 API 客户端 |
| **doc_processor.py** | 文档处理和分块 |
| **index_manager.py** | 索引管理器 |

### 检索模块 (src/retriever/)

| 文件 | 说明 |
|------|------|
| **search_engine.py** | 搜索引擎（统一接口） |
| **vector_search.py** | 向量检索 |
| **keyword_search.py** | 关键词检索（BM25） |
| **hybrid_search.py** | 混合检索（RRF） |

### 存储模块 (src/storage/)

| 文件 | 说明 |
|------|------|
| **vector_store.py** | 向量存储（ChromaDB） |
| **doc_store.py** | 文档存储（JSON） |

### 工具模块 (src/utils/)

| 文件 | 说明 |
|------|------|
| **config.py** | 配置管理 |

### 测试文件 (tests/)

| 文件 | 说明 |
|------|------|
| **test_search.py** | 检索功能测试 |

---

## 📦 其他文件

### 初始化文件

```
src/__init__.py
src/indexer/__init__.py
src/retriever/__init__.py
src/storage/__init__.py
src/utils/__init__.py
```

### 运行时生成的目录

```
data/                    # 数据目录（运行后创建）
├── chromadb/           # ChromaDB 数据
├── processed/          # 处理后的文档
└── raw/                # 原始数据

logs/                    # 日志目录（运行后创建）
└── feishu-pkb.log      # 日志文件
```

---

## 🗺️ 文档导航地图

### 我是新手，从哪里开始？

```
START_HERE.md
    ↓
SETUP_GUIDE.md (配置飞书应用)
    ↓
CHECK_CONFIG.md (检查配置)
    ↓
运行 test_api_access.py
    ↓
QUICKSTART.md (开始使用)
```

### 我遇到了问题

```
CHECK_CONFIG.md (检查配置)
    ↓
SETUP_GUIDE.md (故障排查部分)
    ↓
INSTALLATION.md (安装问题)
    ↓
logs/feishu-pkb.log (查看日志)
```

### 我想深入了解

```
README.md (功能概览)
    ↓
ARCHITECTURE.md (架构设计)
    ↓
DATABASE_COMPARISON.md (技术选型)
    ↓
PROJECT_SUMMARY.md (项目总结)
    ↓
源码阅读 (src/)
```

### 我想定制功能

```
ARCHITECTURE.md (了解架构)
    ↓
config/config.yaml (修改配置)
    ↓
src/ (查看源码)
    ↓
扩展功能
```

---

## 🎯 快速查找

### 我想知道...

**...如何开始？**
→ [START_HERE.md](START_HERE.md)

**...如何配置飞书应用？**
→ [SETUP_GUIDE.md](SETUP_GUIDE.md)

**...为什么不需要安装数据库？**
→ [INSTALLATION.md](INSTALLATION.md) 或 [DATABASE_COMPARISON.md](DATABASE_COMPARISON.md)

**...如何检索？**
→ [QUICKSTART.md](QUICKSTART.md)

**...系统架构是什么样的？**
→ [ARCHITECTURE.md](ARCHITECTURE.md)

**...所有功能有哪些？**
→ [README.md](README.md)

**...技术选型理由？**
→ [DATABASE_COMPARISON.md](DATABASE_COMPARISON.md)

**...项目整体概览？**
→ [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

**...配置项有哪些？**
→ [config/config.yaml](config/config.yaml)

**...如何测试 API 连接？**
→ [test_api_access.py](test_api_access.py)

---

## 📝 文件更新日志

| 日期 | 文件 | 更新内容 |
|------|------|----------|
| 2026-03-06 | 所有文件 | 初始创建 |

---

## 🔗 快速链接

### 外部资源

- [飞书开放平台](https://open.feishu.cn/)
- [Wiki API 文档](https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/wiki-overview)
- [ChromaDB 文档](https://docs.trychroma.com/)
- [sentence-transformers 文档](https://www.sbert.net/)

### 项目文件

- [requirements.txt](requirements.txt) - 依赖列表
- [Makefile](Makefile) - 常用命令
- [skill.yaml](skill.yaml) - Skill 配置
- [.env.example](.env.example) - 配置模板

---

## 💡 提示

### 首次使用推荐阅读顺序

1. **START_HERE.md** - 了解整体流程
2. **SETUP_GUIDE.md** - 配置飞书应用
3. **CHECK_CONFIG.md** - 检查配置
4. 运行 `test_api_access.py` - 测试连接
5. **QUICKSTART.md** - 开始使用

### 遇到问题时

1. **CHECK_CONFIG.md** - 检查配置是否正确
2. **SETUP_GUIDE.md** - 查看故障排查部分
3. 查看日志文件 `logs/feishu-pkb.log`
4. 提交 GitHub Issue

### 深入学习时

1. **ARCHITECTURE.md** - 理解系统架构
2. **DATABASE_COMPARISON.md** - 了解技术选型
3. 阅读源码 `src/`
4. 查看配置 `config/config.yaml`

---

**当前版本**: 1.0.0
**文档总数**: 11 个 Markdown 文件
**代码文件**: 13 个 Python 文件
**配置文件**: 5 个配置文件
