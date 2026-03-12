# 📚 飞书知识库全量更新完整流程

## 🎯 概述

全量更新是从飞书知识空间获取所有知识并构建完整的离线索引的过程。

---

## 🔄 完整流程图

```
用户配置 (.env)
    ↓
[步骤1] 获取知识库结构
    ├─ 递归遍历所有节点
    ├─ 缓存节点列表
    └─ 发现所有文档
    ↓
[步骤2] 下载文档内容
    ├─ 批量下载文档
    ├─ 支持断点续传
    └─ 保存原始内容
    ↓
[步骤3] 智能分块
    ├─ 按标题层级分块
    ├─ 保持上下文完整
    └─ 生成文档块
    ↓
[步骤4] 生成向量
    ├─ TF-IDF 向量化
    ├─ 或 m3e-base 模型
    └─ 768维向量
    ↓
[步骤5] 构建索引
    ├─ 向量索引 (vectors.npz)
    ├─ BM25索引 (bm25_index.pkl)
    └─ SQLite数据库 (kb_data.db)
    ↓
[步骤6] 保存元数据
    └─ metadata.json
    ↓
✅ 离线知识库就绪
```

---

## 📋 详细流程说明

### **第一阶段：准备工作**

#### 1.1 配置飞书凭证

创建或编辑 `.env` 文件：

```bash
# 飞书应用凭证（必需）
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 知识库空间ID（必需）
FEISHU_WIKI_SPACE_ID=xxxxxxxxxx

# 知识库根文档Token（可选，系统会自动尝试）
FEISHU_WIKI_TOKEN=N9kgwANVwifcisk9UT6cDOFInRe
```

**如何获取这些凭证？**

1. **FEISHU_APP_ID & FEISHU_APP_SECRET**
   - 登录飞书开放平台：https://open.feishu.cn
   - 创建或选择企业自建应用
   - 在"凭证与基础信息"页面获取

2. **FEISHU_WIKI_SPACE_ID**
   ```bash
   # 方式1: 使用辅助脚本
   python3 find_space_id.py

   # 方式2: 从知识库URL提取
   python3 get_space_id_from_url.py <知识库URL>
   ```

3. **FEISHU_WIKI_TOKEN**（可选）
   - 从知识库首页URL获取
   - 或使用默认值，系统会自动尝试

#### 1.2 配置应用权限

飞书应用需要以下权限：

- ✅ `docx:document` - 查看文档
- ✅ `docx:document:readonly` - 读取文档内容
- ✅ `wiki:wiki` - 查看知识库
- ✅ `wiki:wiki:readonly` - 读取知识库内容

**配置步骤：**
1. 进入飞书开放平台 → 你的应用
2. 点击"权限管理"
3. 搜索并开通上述权限
4. 点击"版本管理与发布" → 发布新版本

---

### **第二阶段：获取知识库内容**

有两种方式：**简单模式**和**完整模式**

#### 方式 A：简单模式（推荐首次使用）

**适用场景：**
- 知识库只有1个或少数几个文档
- 知识库Token可以直接访问文档内容
- 快速测试

**执行命令：**
```bash
python3 fetch_wiki_content.py
```

**工作流程：**
```
1. 读取 .env 配置
2. 初始化飞书客户端
3. 尝试获取文档：
   ├─ 方法1: 通过 Wiki Token 获取节点
   ├─ 方法2: 通过 Space ID 列举文档
   └─ 方法3: 直接作为文档ID获取
4. 保存到 data/raw/wiki_content.txt
```

**示例输出：**
```
======================================================================
从飞书获取知识库内容
======================================================================

✅ APP_ID: cli_a5b3c...

[步骤1] 获取Wiki节点信息...
✅ 节点信息:
   类型: docx
   Space ID: xxxxxxxxxx
   Obj Token: doxcnxxxxxxxxx

[获取] 文档内容: doxcnxxxxxxxxx
   ✅ 成功 (125680 字符)

======================================================================
✅ 成功保存内容！
======================================================================
文件: data/raw/wiki_content.txt
大小: 125680 字符
```

**生成文件：**
- `data/raw/wiki_content.txt` - 文档原始内容

---

#### 方式 B：完整模式（大型知识库）

**适用场景：**
- 知识库有成百上千个文档
- 需要获取完整的知识库结构
- 支持断点续传

**执行命令：**
```bash
# 完整模式
python3 learn_full_kb.py

# 测试模式（只下载前10个文档）
python3 learn_full_kb.py --test

# 限制数量
python3 learn_full_kb.py --limit 100
```

**工作流程：**
```
阶段1: 获取文档节点列表
├─ 递归遍历知识库空间
├─ 获取所有文档节点（docx类型）
├─ 缓存到 nodes_cache.json
└─ 示例：发现 1597 个文档

阶段2: 批量下载文档内容
├─ 逐个调用飞书API获取文档内容
├─ 显示实时进度：[123/1597] 文档标题 ... ✅
├─ 每10个文档保存一次进度（断点续传）
├─ 自动延迟0.1秒（避免限流）
└─ 合并所有文档内容

阶段3: 保存结果
├─ 保存到 full_kb_content.txt
├─ 生成元数据 full_kb_metadata.json
└─ 记录完成进度 download_progress.json
```

**示例输出：**
```
🔍 递归获取知识库所有节点...
✅ 发现 1597 个文档节点

📥 开始下载文档内容...
总计: 1597 个文档
已完成: 0 个
剩余: 1597 个
======================================================================

[1/1597] 产品知识库首页 ... ✅ 12580 字符
[2/1597] 扫码王产品说明 ... ✅ 8934 字符
[3/1597] 收钱吧APP功能 ... ✅ 15672 字符
...
[1597/1597] 海外业务总结 ... ✅ 9234 字符

======================================================================
下载完成:
  成功: 1597 个
  跳过: 0 个（已下载）
  失败: 0 个
  总计: 1597 个

💾 保存文档内容...
✅ 保存完成: data/raw/full_kb_content.txt
   文档数: 1597
   总字符: 3,126,450
   文件大小: 2.98 MB
```

**生成文件：**
- `data/raw/full_kb_content.txt` - 所有文档合并的内容
- `data/raw/full_kb_metadata.json` - 文档元数据（标题、Token、长度）
- `data/raw/nodes_cache.json` - 节点列表缓存
- `data/raw/download_progress.json` - 下载进度（断点续传）

**断点续传：**
- 如果下载过程中断（Ctrl+C 或网络问题）
- 再次运行 `python3 learn_full_kb.py`
- 会自动跳过已下载的文档，从断点继续

---

### **第三阶段：构建离线索引**

#### 3.1 执行索引构建

**命令：**
```bash
# 如果使用简单模式（fetch_wiki_content.py）
python3 build_offline_kb_fast.py

# 如果使用完整模式（learn_full_kb.py）
python3 build_full_kb_index.py
```

**工作流程：**
```
1. 读取原始内容
   ├─ 加载 wiki_content.txt 或 full_kb_content.txt
   └─ 示例：3,126,450 字符

2. 智能分块
   ├─ 使用 SmartChunker
   ├─ 按标题层级分块
   ├─ 保持上下文完整
   ├─ chunk_size: 512 字符
   ├─ chunk_overlap: 50 字符
   └─ 生成 7,507 个文档块

3. 生成向量嵌入
   ├─ 尝试加载 m3e-base 模型
   ├─ 如果失败，使用 TF-IDF
   ├─ 批量编码（batch_size=32）
   ├─ 归一化向量
   └─ 生成 7,507 × 768 维向量矩阵

4. 构建关键词索引
   ├─ 使用 jieba 分词
   ├─ 构建 BM25Okapi 索引
   └─ 支持中文关键词搜索

5. 保存到数据库
   ├─ SQLite 数据库：kb_data.db
   ├─ 表结构：chunks (7个字段)
   └─ 索引：embedding_index

6. 保存索引文件
   ├─ vectors.npz (压缩的向量矩阵)
   ├─ bm25_index.pkl (BM25索引)
   ├─ tfidf_vectorizer.pkl (TF-IDF向量化器，如果使用)
   └─ metadata.json (元数据)
```

**示例输出：**
```
======================================================================
🚀 快速构建离线知识库
======================================================================

[1] 读取知识库内容...
✅ 加载完成: 3126450 字符

[2] 智能分块...
✅ 生成 7507 个文档块

[3] 加载Embedding模型...
   尝试使用 m3e-base (通过镜像)...
✅ m3e-base 模型加载成功

[4] 生成向量嵌入...
Batches: 100%|████████████| 235/235 [02:34<00:00,  1.52it/s]
✅ 向量生成完成: (7507, 768)

[5] 保存索引...
   ✅ 向量已保存
   ✅ BM25索引已保存
   ✅ 数据库已保存
   ✅ 元数据已保存

======================================================================
✅ 离线知识库构建完成！
======================================================================

数据统计:
  - 文档块数: 7507
  - 向量维度: 768
  - 总字符数: 3126450

测试命令:
  python3 test_search.py
```

**生成文件：**
```
data/
├── vectors.npz              # 压缩的向量矩阵 (~30 MB)
├── bm25_index.pkl          # BM25索引 (~5 MB)
├── tfidf_vectorizer.pkl    # TF-IDF向量化器 (~3 MB)
├── kb_data.db              # SQLite数据库 (~10 MB)
└── metadata.json           # 索引元数据 (~1 KB)

总计: ~50 MB
```

---

### **第四阶段：验证和测试**

#### 4.1 验证系统状态

```bash
python3 verify_system.py
```

**检查项：**
- ✅ 配置文件完整性
- ✅ 飞书API连接
- ✅ 索引文件存在
- ✅ 数据库完整性
- ✅ 搜索引擎加载

#### 4.2 测试搜索功能

```bash
# 简单测试
python3 test_simple_search.py

# 测试不同模式
python3 test_search.py

# 使用 Skill 命令
python3 skill_main.py search 扫码王
python3 skill_main.py search 扫码王 --mode hybrid --top-k 5
```

#### 4.3 查看知识库状态

```bash
python3 skill_main.py status
```

**示例输出：**
```
📊 知识库状态
======================================================================
构建时间: 2026-03-12 10:30:15
文档块数: 7507
向量维度: 768
模型: moka-ai/m3e-base or TF-IDF

文件大小:
  vectors: 30.2 MB
  bm25: 4.8 MB
  database: 9.6 MB
  content: 2.9 MB

搜索引擎: loaded
```

---

## 🔄 更新策略对比

### 全量更新 vs 增量学习

| 特性 | 全量更新 (`update`) | 增量学习 (`learn`) |
|------|-------------------|------------------|
| **时间** | 10-30分钟 | 3-15秒 |
| **数据源** | 整个知识库空间 | 单个文档 URL/ID |
| **影响范围** | 重建所有索引 | 仅追加新内容 |
| **适用场景** | 初始部署、定期同步 | 添加新文档 |
| **断点续传** | ✅ 支持 | N/A |
| **网络流量** | 大（所有文档） | 小（单个文档） |

### 推荐工作流

```bash
# 1. 初始部署：全量更新
/feishu-kb update

# 2. 日常使用：增量学习
/feishu-kb learn <新文档URL>

# 3. 定期同步：全量更新（每周/每月）
/feishu-kb update
```

---

## 📊 文件结构总览

```
Feishu PKB/
├── .env                              # 配置文件（凭证）
│
├── data/                             # 数据目录
│   ├── raw/                          # 原始数据
│   │   ├── wiki_content.txt          # 简单模式：文档内容
│   │   ├── full_kb_content.txt       # 完整模式：所有文档
│   │   ├── full_kb_metadata.json     # 文档元数据
│   │   ├── nodes_cache.json          # 节点列表缓存
│   │   ├── download_progress.json    # 下载进度
│   │   └── learned/                  # 增量学习的文档
│   │       ├── learned_doc1.txt
│   │       └── learned_doc2.txt
│   │
│   ├── vectors.npz                   # 向量索引
│   ├── bm25_index.pkl               # BM25索引
│   ├── tfidf_vectorizer.pkl         # TF-IDF向量化器
│   ├── kb_data.db                   # SQLite数据库
│   └── metadata.json                # 索引元数据
│
├── fetch_wiki_content.py            # 简单模式：获取文档
├── learn_full_kb.py                 # 完整模式：批量下载
├── build_offline_kb_fast.py         # 构建索引（简单）
├── build_full_kb_index.py           # 构建索引（完整）
├── learn_document.py                # 增量学习：单个文档
├── incremental_index.py             # 增量索引更新
│
└── skill_main.py                    # Skill 主入口
```

---

## ⚙️ 配置文件说明

### config/config.yaml

控制分块和检索行为：

```yaml
indexing:
  chunking:
    strategy: recursive        # 分块策略
    chunk_size: 512           # 块大小（字符）
    chunk_overlap: 50         # 重叠大小
    separators:               # 分隔符优先级
      - "\n## "               # 二级标题
      - "\n### "              # 三级标题
      - "\n#### "             # 四级标题
      - "\n\n"                # 段落
      - "\n"                  # 行
      - "。"                  # 句子

retrieval:
  vector_search:
    top_k: 20                 # 向量检索数量
    similarity_threshold: 0.3 # 相似度阈值

  keyword_search:
    top_k: 20                 # 关键词检索数量

  hybrid:
    vector_weight: 0.5        # 向量权重
    keyword_weight: 0.5       # 关键词权重
    k: 60                     # RRF融合参数
```

---

## 🐛 常见问题

### Q1: 获取文档失败 - 权限不足

**错误：**
```
❌ 失败: [99991663] No permission
```

**解决：**
1. 检查应用权限是否开通
2. 确认应用是否已发布
3. 检查知识库是否对应用可见

### Q2: Space ID 不正确

**错误：**
```
❌ 备用方法也失败: space not found
```

**解决：**
```bash
# 重新获取正确的 Space ID
python3 find_space_id.py
python3 get_space_id_from_url.py <知识库URL>
```

### Q3: 下载过程中断

**解决：**
```bash
# 直接重新运行，会从断点继续
python3 learn_full_kb.py

# 或查看进度
cat data/raw/download_progress.json
```

### Q4: 向量生成很慢

**原因：** m3e-base 模型下载慢或加载失败

**解决：**
- 系统会自动降级到 TF-IDF（速度更快）
- 或设置镜像：`export HF_ENDPOINT=https://hf-mirror.com`

### Q5: 内存不足

**错误：**
```
MemoryError: Unable to allocate array
```

**解决：**
```bash
# 分批处理，减少一次处理的文档数
python3 learn_full_kb.py --limit 500
# 多次运行，每次500个文档
```

---

## 📈 性能优化

### 加速下载

```python
# 在 learn_full_kb.py 中调整
time.sleep(0.1)  # 减小延迟（注意API限流）
```

### 并行处理

```bash
# 使用更大的 batch_size
# 在 build_offline_kb_fast.py 中修改
batch_size=64  # 默认32
```

### 磁盘空间优化

```bash
# 构建完成后可以删除原始内容
rm data/raw/wiki_content.txt
rm data/raw/full_kb_content.txt

# 保留索引文件即可正常搜索
```

---

## 🎯 总结

### 核心流程

```
配置凭证 → 获取内容 → 构建索引 → 测试验证
```

### 一键全量更新

```bash
# 最简单的方式
python3 skill_main.py update
```

这个命令会自动执行：
1. fetch_wiki_content.py
2. build_offline_kb_fast.py
3. 重新加载搜索引擎

### 下一步

- 查看 [INCREMENTAL_LEARNING_GUIDE.md](INCREMENTAL_LEARNING_GUIDE.md) 了解增量学习
- 查看 [OPENCLAW_SKILL_GUIDE.md](OPENCLAW_SKILL_GUIDE.md) 了解 OpenClaw 集成
- 查看 [README.md](README.md) 了解项目概述

---

**版本：** 1.3.0
**最后更新：** 2026-03-12
