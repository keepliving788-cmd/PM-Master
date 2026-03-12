# 快速开始指南

## 5 分钟快速上手

### 步骤 1: 克隆并安装

```bash
# 进入项目目录
cd "Feishu PKB"

# 安装依赖
pip install -r requirements.txt

# 初始化环境
make setup
```

### 步骤 2: 配置飞书应用

1. **创建飞书应用**
   - 访问 https://open.feishu.cn/
   - 创建企业自建应用
   - 获取 App ID 和 App Secret

2. **配置权限**
   - 开启权限：
     - `wiki:wiki:readonly` - 知识库读取
     - `docx:document:readonly` - 文档读取

3. **配置环境变量**
   ```bash
   # 编辑 .env 文件
   FEISHU_APP_ID=cli_xxx
   FEISHU_APP_SECRET=xxx
   FEISHU_WIKI_SPACE_ID=N9kgwANVwifcisk9UT6cDOFInRe
   ```

### 步骤 3: 构建索引

```bash
# 全量构建索引（首次运行）
python src/main.py index --full

# 这将：
# 1. 从飞书下载所有文档
# 2. 分块处理文档
# 3. 构建向量索引（本地）
# 4. 构建关键词索引
```

### 步骤 4: 开始检索

```bash
# 基本检索
python src/main.py search "如何使用产品"

# 指定检索模式
python src/main.py search "技术架构" --mode=hybrid --top-k=10

# 查看文档详情
python src/main.py view <doc-id>

# 查看统计信息
python src/main.py stats
```

## 在 OpenClaw 中使用

### 加载 Skill

```bash
# 假设 OpenClaw 支持加载本地 skills
/skill load /path/to/feishu-pkb-skill

# 或者如果已安装到 skills 目录
/skill load feishu-pkb-retrieval
```

### 使用示例

```bash
# 检索知识库
/feishu-pkb search "产品使用指南"

# 同步最新内容
/feishu-pkb sync

# 查看统计
/feishu-pkb stats
```

## 检索模式对比

### Vector Search (向量检索)
- 语义相似度匹配
- 适合：概念性查询、同义词查询
- 示例：`python src/main.py search "如何提升性能" --mode=vector`

### Keyword Search (关键词检索)
- BM25 算法
- 适合：精确关键词匹配
- 示例：`python src/main.py search "API endpoint" --mode=keyword`

### Hybrid Search (混合检索) ⭐ 推荐
- 结合向量和关键词的优势
- RRF 融合算法
- 适合：大多数场景
- 示例：`python src/main.py search "技术文档" --mode=hybrid`

## 高级用法

### 增量同步

```bash
# 只更新有变化的文档
python src/main.py sync
```

### 自定义配置

编辑 `config/config.yaml`:

```yaml
# 调整分块大小
indexing:
  chunking:
    chunk_size: 1024  # 默认 512
    chunk_overlap: 100  # 默认 50

# 调整检索权重
retrieval:
  weights:
    vector: 0.7  # 向量权重
    keyword: 0.3  # 关键词权重
```

### 使用 Makefile

```bash
# 查看所有命令
make help

# 一键构建索引
make index

# 增量同步
make sync

# 交互式检索
make search
```

## 故障排查

### 问题 1: 无法连接飞书 API

**解决方法：**
1. 检查网络连接
2. 确认 App ID 和 App Secret 正确
3. 确认应用权限已开启
4. 查看日志：`tail -f logs/feishu-pkb.log`

### 问题 2: 模型下载慢

**解决方法：**
```bash
# 手动下载模型
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
```

### 问题 3: 内存不足

**解决方法：**
- 减小 batch_size
- 减小 chunk_size
- 分批处理文档

## 下一步

- 阅读完整文档：`README.md`
- 查看配置选项：`config/config.yaml`
- 探索源代码：`src/`
- 提交问题：GitHub Issues

## 性能参考

**测试环境：**
- 文档数：100 篇
- 总字符数：500K
- 硬件：M1 Mac, 16GB RAM

**性能指标：**
- 索引构建：~5 分钟
- 向量检索：~50ms
- 混合检索：~100ms
- 内存占用：~2GB

---

🎉 现在你已经可以开始使用飞书产品知识库离线检索了！
