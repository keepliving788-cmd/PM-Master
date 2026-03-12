# 🚀 从这里开始

欢迎使用飞书产品知识库离线检索 Skill！

## 📝 开始前须知

### 关于数据库
✅ **无需安装独立数据库！** 所有依赖通过 `pip install` 即可。

ChromaDB 是嵌入式数据库（类似 SQLite），直接集成在应用中。

### 关于知识库访问
⚠️ **需要配置飞书应用！** 代码通过飞书 Open API 访问知识库，不是直接读取网页。

你需要：
1. 创建飞书企业自建应用
2. 配置权限
3. 获取应用凭证

---

## 🎯 快速开始（3 步）

### 第 1 步：安装依赖

```bash
cd "Feishu PKB"

# 安装所有依赖（包括 ChromaDB）
pip install -r requirements.txt

# 初始化目录
make setup
# 或手动创建：mkdir -p data/{raw,processed,chromadb} logs
```

### 第 2 步：配置飞书应用

**详细指南：** 请阅读 [SETUP_GUIDE.md](SETUP_GUIDE.md)

**快速步骤：**
1. 访问 https://open.feishu.cn/
2. 创建企业自建应用
3. 添加权限：
   - `wiki:wiki:readonly`
   - `docx:document:readonly`
4. 发布应用
5. 获取 App ID 和 App Secret

**配置文件：**
```bash
cp .env.example .env
nano .env  # 填入你的 App ID 和 App Secret
```

### 第 3 步：测试连接

```bash
# 运行测试脚本
python test_api_access.py
```

**预期输出：**
```
✅ App ID: cli_xxxxxx...
✅ App Secret: ********************
✅ 成功获取 10 个节点
🎉 测试通过！
```

---

## ✅ 测试通过后

### 构建索引

```bash
# 全量构建索引（首次运行）
python src/main.py index --full
```

这会：
1. 从飞书下载所有文档
2. 处理和分块文档
3. 构建向量索引（ChromaDB）
4. 构建关键词索引（BM25）

**耗时：** 约 5-30 分钟（取决于文档数量）

### 开始检索

```bash
# 基础检索
python src/main.py search "如何使用产品"

# 混合检索（推荐）
python src/main.py search "技术文档" --mode=hybrid --top-k=10

# 查看统计
python src/main.py stats
```

---

## 📚 文档导航

### 必读文档

| 文档 | 内容 | 适合 |
|------|------|------|
| **[SETUP_GUIDE.md](SETUP_GUIDE.md)** | 飞书应用配置详细指南 | 首次配置 |
| **[CHECK_CONFIG.md](CHECK_CONFIG.md)** | 配置检查清单 | 测试前检查 |
| **[INSTALLATION.md](INSTALLATION.md)** | 安装说明（数据库问题） | 安装疑问 |
| **[QUICKSTART.md](QUICKSTART.md)** | 5分钟快速上手 | 快速开始 |

### 深入了解

| 文档 | 内容 | 适合 |
|------|------|------|
| **[README.md](README.md)** | 完整功能文档 | 全面了解 |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | 架构设计 | 深入理解 |
| **[DATABASE_COMPARISON.md](DATABASE_COMPARISON.md)** | 数据库方案对比 | 技术选型 |
| **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** | 项目总结 | 整体概览 |

---

## 🔧 常用命令

### Makefile 命令

```bash
make help      # 查看所有命令
make install   # 安装依赖
make setup     # 初始化环境
make index     # 构建索引
make sync      # 增量同步
make search    # 交互式检索
make clean     # 清理数据
```

### Python 命令

```bash
# 索引管理
python src/main.py index --full        # 全量索引
python src/main.py index               # 增量索引
python src/main.py sync                # 同步更新

# 检索
python src/main.py search "查询"       # 基础检索
python src/main.py search "查询" --mode=vector    # 向量检索
python src/main.py search "查询" --mode=keyword   # 关键词检索
python src/main.py search "查询" --mode=hybrid    # 混合检索

# 查看
python src/main.py view <doc-id>       # 查看文档
python src/main.py stats               # 统计信息
```

---

## ❓ 常见问题

### Q: 需要安装数据库吗？
**A: 不需要！** ChromaDB 通过 pip 安装，无需单独配置。

### Q: 如何访问飞书知识库？
**A: 通过飞书 Open API。** 需要创建应用并配置权限。详见 [SETUP_GUIDE.md](SETUP_GUIDE.md)

### Q: 测试脚本显示权限错误？
**A: 检查以下几点：**
1. 应用是否已发布
2. 权限是否已开通（`wiki:wiki:readonly`）
3. 等待 1-2 分钟让权限生效

### Q: 检索需要联网吗？
**A: 构建索引时需要（下载文档），检索时不需要（完全离线）。**

### Q: 支持哪些文档格式？
**A: 飞书文档（Docx）、Wiki。** 旧版 Doc 需要先转换。

### Q: 如何更新知识库内容？
**A: 运行 `python src/main.py sync` 进行增量同步。**

---

## 🎓 学习路径

### 初学者

1. ✅ 阅读本文档（START_HERE.md）
2. ✅ 按照 [SETUP_GUIDE.md](SETUP_GUIDE.md) 配置飞书应用
3. ✅ 运行 `test_api_access.py` 测试
4. ✅ 构建索引并开始检索
5. ✅ 阅读 [QUICKSTART.md](QUICKSTART.md) 了解更多用法

### 进阶用户

1. ✅ 阅读 [ARCHITECTURE.md](ARCHITECTURE.md) 了解架构
2. ✅ 修改 `config/config.yaml` 自定义配置
3. ✅ 查看源码了解实现细节
4. ✅ 扩展功能（新增检索模式、存储后端等）

### 问题排查

1. ✅ 使用 [CHECK_CONFIG.md](CHECK_CONFIG.md) 检查配置
2. ✅ 查看 [SETUP_GUIDE.md](SETUP_GUIDE.md) 的故障排查部分
3. ✅ 查看日志文件 `logs/feishu-pkb.log`
4. ✅ 提交 GitHub Issue

---

## 🎉 准备好了？

### 立即开始

```bash
# 1. 安装
pip install -r requirements.txt
make setup

# 2. 配置（参考 SETUP_GUIDE.md）
cp .env.example .env
nano .env

# 3. 测试
python test_api_access.py

# 4. 构建
python src/main.py index --full

# 5. 检索
python src/main.py search "你的查询"
```

---

**下一步：** 阅读 [SETUP_GUIDE.md](SETUP_GUIDE.md) 开始配置飞书应用！

**需要帮助？** 查看 [CHECK_CONFIG.md](CHECK_CONFIG.md) 配置检查清单。

**有问题？** 查看各文档的常见问题部分或提交 Issue。

---

**版本**: 1.0.0
**最后更新**: 2026-03-06
**状态**: ✅ 生产就绪
