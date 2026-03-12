# 🔄 知识库更新方式对比

## 📊 三种更新方式

本系统支持三种知识库更新方式，适用于不同场景。

---

## 方式对比表

| 特性 | 🔄 全量更新 (update) | ⚡ 增量学习 (learn) | 📦 完整采集 (full) |
|------|-------------------|------------------|------------------|
| **命令** | `/feishu-kb update` | `/feishu-kb learn <URL>` | `python3 learn_full_kb.py` |
| **适用场景** | 日常同步 | 添加单个文档 | 初始部署 |
| **数据源** | Wiki Space | 单个文档 URL | 整个知识库空间 |
| **时间** | 1-3 分钟 | 3-15 秒 | 10-30 分钟 |
| **文档数** | 当前配置的空间 | 1 个 | 所有文档（如1597个） |
| **网络流量** | 中 | 小 | 大 |
| **断点续传** | ❌ | N/A | ✅ |
| **影响范围** | 重建所有索引 | 追加新内容 | 重建所有索引 |
| **索引方式** | 完全重建 | 增量追加 | 完全重建 |

---

## 📖 详细说明

### 🔄 方式 1：全量更新（常规）

**使用场景：**
- ✅ 日常知识库同步
- ✅ 知识库有少量更新（<100个文档）
- ✅ 快速刷新索引

**命令：**
```bash
# Skill 命令
/feishu-kb update

# 或直接运行
python3 skill_main.py update
```

**工作流程：**
```
1. fetch_wiki_content.py
   ├─ 从 Wiki Space 获取文档
   ├─ 通过 Wiki Token 或 Space ID
   └─ 保存到 wiki_content.txt

2. build_offline_kb_fast.py
   ├─ 读取 wiki_content.txt
   ├─ 智能分块
   ├─ 生成向量
   ├─ 构建 BM25
   └─ 保存索引

3. 重新加载搜索引擎
```

**优点：**
- ⚡ 速度快（1-3分钟）
- 🎯 自动化程度高
- 🔧 配置简单

**缺点：**
- ⚠️  每次完全重建索引
- ⚠️  只能同步配置的知识库空间
- ⚠️  如果中断需要重新开始

**适合：**
- 小型知识库（<100个文档）
- 定期同步（每天/每周）

---

### ⚡ 方式 2：增量学习（推荐）🆕

**使用场景：**
- ✅ 快速添加新文档
- ✅ 无需重建整个索引
- ✅ 测试单个文档

**命令：**
```bash
# Skill 命令
/feishu-kb learn https://xxx.feishu.cn/docx/xxxxx
/feishu-kb learn doxcnxxxxxx

# 或直接运行
python3 skill_main.py learn <文档URL>
```

**工作流程：**
```
1. learn_document.py
   ├─ 解析文档 URL/ID
   ├─ 调用飞书 API
   └─ 保存到 learned/

2. incremental_index.py
   ├─ 加载现有索引
   ├─ 分块新文档
   ├─ 生成向量
   ├─ 合并索引
   │   ├─ 向量追加到 vectors.npz
   │   ├─ 更新 bm25_index.pkl
   │   └─ 插入到 kb_data.db
   └─ 更新元数据

3. 重新加载搜索引擎
```

**优点：**
- ⚡ 极快（3-15秒）
- 🎯 精准控制
- 💡 不影响现有数据
- 🔄 可连续添加多个文档

**缺点：**
- ⚠️  每次只能学习一个文档
- ⚠️  需要文档 URL 或 ID

**适合：**
- 添加新文档
- 更新单个文档
- 快速测试

**示例：**
```bash
# 1. 学习新产品文档
/feishu-kb learn https://sqb.feishu.cn/docx/new_product

# 2. 立即搜索验证
/feishu-kb search 新产品

# 3. 查看更新统计
/feishu-kb status
# 输出：chunk_count: 7507 → 7519 (+12)
```

---

### 📦 方式 3：完整采集（初始化）

**使用场景：**
- ✅ 首次部署系统
- ✅ 大型知识库（数百上千文档）
- ✅ 完整备份知识库

**命令：**
```bash
# 完整模式
python3 learn_full_kb.py

# 测试模式（前10个）
python3 learn_full_kb.py --test

# 限制数量
python3 learn_full_kb.py --limit 100
```

**工作流程：**
```
1. 递归遍历知识库
   ├─ 获取所有节点
   ├─ 缓存到 nodes_cache.json
   └─ 发现 1597 个文档

2. 批量下载文档
   ├─ 逐个下载内容
   ├─ 显示进度条
   ├─ 每10个保存进度
   ├─ 支持断点续传
   └─ 保存到 full_kb_content.txt

3. 构建完整索引
   ├─ python3 build_full_kb_index.py
   ├─ 分块所有文档
   ├─ 生成所有向量
   └─ 构建完整索引
```

**优点：**
- 📚 获取所有文档
- 🔄 断点续传
- 📊 详细进度
- 💾 保存完整内容

**缺点：**
- 🐌 耗时长（10-30分钟）
- 💾 占用空间大
- 🌐 网络流量大

**适合：**
- 首次部署
- 完整备份
- 大规模更新

**示例输出：**
```
🔍 递归获取知识库所有节点...
✅ 发现 1597 个文档节点

📥 开始下载文档内容...
[1/1597] 产品知识库首页 ... ✅ 12580 字符
[2/1597] 扫码王产品说明 ... ✅ 8934 字符
...
[1597/1597] 海外业务总结 ... ✅ 9234 字符

✅ 保存完成: data/raw/full_kb_content.txt
   文档数: 1597
   总字符: 3,126,450
```

---

## 🎯 选择建议

### 场景 1：首次部署

```bash
# 如果知识库很大（>100文档）
python3 learn_full_kb.py
python3 build_full_kb_index.py

# 如果知识库较小
/feishu-kb update
```

### 场景 2：日常维护

```bash
# 添加新文档
/feishu-kb learn <新文档URL>

# 定期全量同步（每周）
/feishu-kb update
```

### 场景 3：快速测试

```bash
# 学习测试文档
/feishu-kb learn https://xxx.feishu.cn/docx/test

# 搜索验证
/feishu-kb search 测试内容
```

### 场景 4：大规模更新

```bash
# 1. 完整采集
python3 learn_full_kb.py

# 2. 构建索引
python3 build_full_kb_index.py

# 3. 后续使用增量学习
/feishu-kb learn <新文档URL>
```

---

## 📊 性能对比

### 时间对比（1个新文档）

```
增量学习：     ▓░░░░░░░░░ 5秒
全量更新：     ▓▓▓▓▓▓▓▓░░ 90秒
完整采集：     ▓▓▓▓▓▓▓▓▓▓ 1800秒
```

### 网络流量对比

```
增量学习：     ▓░░░░░░░░░ <1 MB
全量更新：     ▓▓▓▓░░░░░░ ~10 MB
完整采集：     ▓▓▓▓▓▓▓▓▓▓ ~100 MB
```

### 磁盘写入对比

```
增量学习：     ▓░░░░░░░░░ <10 MB
全量更新：     ▓▓▓▓░░░░░░ ~50 MB
完整采集：     ▓▓▓▓▓▓▓▓▓▓ ~150 MB
```

---

## 🔄 工作流建议

### 推荐工作流 A（轻量级）

```bash
# 1. 初始部署
/feishu-kb update

# 2. 日常添加新文档
/feishu-kb learn <文档URL>

# 3. 每周全量同步
/feishu-kb update
```

**适合：**
- 小型团队
- 文档数量 <100
- 更新频率低

### 推荐工作流 B（重量级）

```bash
# 1. 初始部署
python3 learn_full_kb.py
python3 build_full_kb_index.py

# 2. 日常添加新文档
/feishu-kb learn <文档URL>

# 3. 每月全量同步
python3 learn_full_kb.py
python3 build_full_kb_index.py
```

**适合：**
- 大型团队
- 文档数量 >500
- 知识库频繁更新

---

## 💡 最佳实践

### 1. 组合使用

```bash
# 首次：完整采集
python3 learn_full_kb.py

# 日常：增量学习
/feishu-kb learn <新文档>

# 定期：全量更新
/feishu-kb update  # 每周
```

### 2. 监控知识库

```bash
# 查看状态
/feishu-kb status

# 记录块数变化
# 7507 → 7519 → 7532 ...
```

### 3. 定时任务

```bash
# crontab
# 每天2点：增量学习新文档（如果有）
0 2 * * * cd /path/to/skill && /feishu-kb learn <文档URL>

# 每周日：全量更新
0 3 * * 0 cd /path/to/skill && /feishu-kb update
```

---

## 🆚 对比总结

### 何时使用全量更新？

✅ 知识库有多个文档更新
✅ 需要同步整个知识库空间
✅ 可以接受1-3分钟的等待
✅ 定期同步（每天/每周）

### 何时使用增量学习？

✅ 只有1-2个新文档
✅ 需要快速生效（几秒钟）
✅ 文档不在配置的知识库空间
✅ 测试文档是否可搜索

### 何时使用完整采集？

✅ 首次部署系统
✅ 知识库有数百上千文档
✅ 需要完整备份
✅ 大规模重建索引

---

## 📚 相关文档

- [FULL_UPDATE_WORKFLOW.md](FULL_UPDATE_WORKFLOW.md) - 全量更新详细流程
- [INCREMENTAL_LEARNING_GUIDE.md](INCREMENTAL_LEARNING_GUIDE.md) - 增量学习使用指南
- [README.md](README.md) - 项目概述

---

**版本：** 1.3.0
**最后更新：** 2026-03-12
