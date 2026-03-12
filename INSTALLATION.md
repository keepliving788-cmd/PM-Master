# 安装指南

## ✅ 无需单独安装数据库！

这个方案使用 **嵌入式数据库**，所有依赖通过 pip 安装即可，无需配置额外的数据库服务器。

## 系统要求

### 基础要求
- **Python**: 3.9 或更高版本
- **内存**: 建议 4GB 以上
- **磁盘**: 建议 5GB 以上可用空间
- **操作系统**: macOS / Linux / Windows

### Python 版本检查
```bash
python --version  # 应该显示 3.9 或更高
```

## 安装步骤

### 方式一：使用 Makefile（推荐）

```bash
# 1. 进入项目目录
cd "Feishu PKB"

# 2. 安装所有依赖
make install

# 3. 初始化环境
make setup

# 完成！无需其他步骤
```

### 方式二：手动安装

```bash
# 1. 进入项目目录
cd "Feishu PKB"

# 2. （推荐）创建虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate    # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 创建必要的目录
mkdir -p data/{raw,processed,chromadb}
mkdir -p logs

# 5. 复制环境变量模板
cp .env.example .env

# 完成！
```

## 依赖说明

### 核心依赖（自动安装）

| 包名 | 版本 | 用途 | 安装类型 |
|------|------|------|----------|
| **chromadb** | >=0.4.0 | 向量数据库（嵌入式） | pip 安装 |
| **sentence-transformers** | >=2.2.0 | Embedding 模型 | pip 安装 |
| **lark-oapi** | >=1.2.0 | 飞书 API SDK | pip 安装 |
| **rank-bm25** | >=0.2.0 | BM25 算法 | pip 安装 |

### ChromaDB 说明

**ChromaDB 是嵌入式数据库，类似于 SQLite：**

```python
# 安装后直接在代码中使用
import chromadb

# 创建客户端（无需启动服务）
client = chromadb.PersistentClient(path="./data/chromadb")

# 数据自动保存到本地文件
```

**工作原理：**
```
pip install chromadb
       ↓
ChromaDB Python 包
       ↓
直接在进程内运行
       ↓
数据保存到 data/chromadb/
```

**不是这样的（不需要）：**
```
✗ 启动 ChromaDB 服务器
✗ 配置数据库连接
✗ 管理数据库实例
```

## 数据存储结构

安装完成后，数据将存储在以下位置：

```
Feishu PKB/
└── data/
    ├── chromadb/              # ChromaDB 数据（自动创建）
    │   ├── chroma.sqlite3     # 元数据
    │   └── ...                # 向量数据
    ├── processed/             # 文档 JSON 文件
    │   ├── index.json
    │   └── *.json
    └── raw/                   # 原始数据（可选）
```

## 验证安装

### 检查 Python 依赖
```bash
# 检查关键包是否安装成功
python -c "import chromadb; print('ChromaDB:', chromadb.__version__)"
python -c "import sentence_transformers; print('sentence-transformers: OK')"
python -c "import lark_oapi; print('lark-oapi: OK')"
```

### 检查目录结构
```bash
ls -la data/
# 应该显示: chromadb/, processed/, raw/
```

### 运行测试
```bash
# 查看帮助
python src/main.py --help

# 查看版本
python src/main.py stats
```

## 首次运行

### 1. 配置飞书凭证

编辑 `.env` 文件：
```bash
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
FEISHU_WIKI_SPACE_ID=N9kgwANVwifcisk9UT6cDOFInRe
```

### 2. 下载 Embedding 模型

第一次运行时，会自动下载 Embedding 模型（约 470MB）：

```bash
# 执行任何命令都会触发下载
python src/main.py stats

# 模型会缓存到 ~/.cache/huggingface/
```

**模型下载位置：**
```
~/.cache/huggingface/hub/
└── models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2/
```

### 3. 构建索引

```bash
# 构建第一个索引
python src/main.py index --full

# 数据会自动保存到 data/ 目录
```

## 磁盘空间估算

| 组件 | 大小（约） | 说明 |
|------|-----------|------|
| Python 依赖 | 1.5 GB | 包括 PyTorch |
| Embedding 模型 | 470 MB | 首次下载 |
| 100 篇文档数据 | 100 MB | 包括向量和原文 |
| **总计** | **~2 GB** | 首次安装 |

## 常见问题

### Q1: 安装 ChromaDB 失败？

**问题：**
```
ERROR: Failed building wheel for chromadb
```

**解决：**
```bash
# 升级 pip
pip install --upgrade pip setuptools wheel

# 重新安装
pip install chromadb
```

### Q2: sentence-transformers 下载慢？

**解决：** 使用镜像源
```bash
# 方式 1: 设置环境变量
export HF_ENDPOINT=https://hf-mirror.com

# 方式 2: 使用国内镜像
pip install -U huggingface_hub
```

### Q3: PyTorch 安装问题？

**解决：**
```bash
# CPU 版本（更小更快）
pip install torch --index-url https://download.pytorch.org/whl/cpu

# 或者使用 conda
conda install pytorch cpuonly -c pytorch
```

### Q4: M1/M2 Mac 兼容性？

**解决：** 完全兼容！
```bash
# 确保使用 ARM64 版本的 Python
python -c "import platform; print(platform.machine())"
# 应该显示: arm64

# 所有依赖都支持 Apple Silicon
```

### Q5: Windows 安装问题？

**常见问题：**
- 缺少 C++ 编译器

**解决：**
```bash
# 1. 安装 Visual Studio Build Tools
# 下载: https://visualstudio.microsoft.com/downloads/

# 2. 或使用预编译的包
pip install --only-binary :all: chromadb
```

## 卸载

### 完全卸载
```bash
# 1. 删除虚拟环境
rm -rf venv/

# 2. 删除数据
rm -rf data/ logs/

# 3. 删除模型缓存（可选）
rm -rf ~/.cache/huggingface/
```

### 仅清理数据
```bash
# 使用 Makefile
make clean

# 或手动删除
rm -rf data/ logs/
```

## 性能优化

### 加速模型下载
```bash
# 设置镜像（中国大陆用户）
export HF_ENDPOINT=https://hf-mirror.com
```

### 减少内存占用
编辑 `config/config.yaml`:
```yaml
indexing:
  embedding:
    batch_size: 16  # 默认 32，减小可降低内存
```

### GPU 加速（可选）
```bash
# 如果有 NVIDIA GPU
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 升级

### 升级依赖
```bash
pip install --upgrade -r requirements.txt
```

### 迁移数据
```bash
# 备份旧数据
cp -r data/ data.backup/

# 升级后重建索引（如果格式变化）
python src/main.py index --full --force
```

## 网络要求

### 需要网络的操作：
- ✅ 安装依赖（pip install）
- ✅ 下载 Embedding 模型（首次）
- ✅ 构建索引（从飞书下载文档）

### 无需网络的操作：
- ✅ 检索查询（完全离线）
- ✅ 查看文档
- ✅ 统计信息

## 下一步

安装完成后：

1. **配置**: 编辑 `.env` 文件
2. **构建**: `python src/main.py index --full`
3. **使用**: `python src/main.py search "查询"`

参考文档：
- **快速开始**: `QUICKSTART.md`
- **完整文档**: `README.md`
- **架构设计**: `ARCHITECTURE.md`

---

**有问题？** 查看故障排查部分或提交 Issue
