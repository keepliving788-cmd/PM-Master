# 飞书知识库增量更新方案设计

## 📋 背景

当前系统包含1597个文档，首次学习需要10-30分钟。在生产环境中，知识库可能每周都有更新，需要一个高效的增量更新机制。

## 🎯 设计目标

1. **减少更新时间**：只处理变化的文档
2. **保证数据一致性**：索引与知识库同步
3. **实现简单可靠**：易于维护和调试
4. **支持断点续传**：更新过程可中断恢复

## 🔍 现状分析

### 当前更新机制

- **全量更新**：重新运行 `learn_full_kb.py`
- **时间成本**：10-30分钟（1597个文档）
- **网络请求**：~1600次API调用
- **索引重建**：完整重建TF-IDF + BM25索引

### 系统约束

1. **飞书API限制**：
   - 可能没有文档修改时间字段
   - 无法批量获取文档元数据
   - 需要逐个获取文档内容

2. **索引特性**：
   - TF-IDF依赖全局词频统计
   - BM25依赖全局文档频率
   - 增量更新索引非常复杂

## 💡 方案对比

### 方案A：时间戳对比增量更新

#### 实现思路

```python
class IncrementalUpdater:
    def check_updates(self):
        """检查文档变更"""
        # 1. 读取上次更新时间
        last_update = self._load_last_update()

        # 2. 获取所有文档节点
        current_nodes = learner.get_all_nodes()

        # 3. 对比找出差异
        old_docs = {doc['obj_token']: doc for doc in last_update['documents']}

        new_docs = []      # 新增的文档
        updated_docs = []  # 可能更新的文档
        deleted_docs = []  # 删除的文档

        current_tokens = set()
        for node in current_nodes:
            token = node['obj_token']
            current_tokens.add(token)

            if token not in old_docs:
                new_docs.append(node)
            else:
                # 需要重新获取内容对比
                updated_docs.append(node)

        # 找出已删除的文档
        for token in old_docs:
            if token not in current_tokens:
                deleted_docs.append(token)

        return {
            'new': new_docs,
            'updated': updated_docs,
            'deleted': deleted_docs
        }

    def incremental_update(self):
        """增量更新"""
        changes = self.check_updates()

        # 下载变更的文档
        docs_to_fetch = changes['new'] + changes['updated']
        contents = learner.download_all_documents(docs_to_fetch)

        # 重建索引（仍需全量）
        self._rebuild_index(contents, changes['deleted'])
```

#### 优点
- ✅ 只下载变化的文档，节省网络时间
- ✅ 可以检测到删除的文档
- ✅ 逻辑清晰

#### 缺点
- ❌ 飞书API可能不提供文档修改时间
- ❌ 索引仍需全量重建（TF-IDF/BM25依赖全局统计）
- ❌ 实现复杂度高
- ❌ 难以判断文档是否真的更新了

#### 适用场景
- 知识库变化频繁（每天更新）
- 每次只有少量文档变化（<10%）
- 有明确的文档版本信息

---

### 方案B：内容哈希对比

#### 实现思路

```python
def check_content_changes(self):
    """通过哈希对比内容是否变化"""
    # 1. 加载旧的文档哈希
    old_hashes = self._load_content_hashes()

    # 2. 获取所有文档，计算新哈希
    nodes = learner.get_all_nodes()

    changed_docs = []
    for node in nodes:
        obj_token = node['obj_token']

        # 仍需下载内容来计算哈希
        content = learner._fetch_document(obj_token)
        current_hash = hashlib.md5(content.encode()).hexdigest()

        old_hash = old_hashes.get(obj_token)

        if old_hash != current_hash:
            changed_docs.append(node)
            old_hashes[obj_token] = current_hash

    return changed_docs
```

#### 优点
- ✅ 精确检测内容变化
- ✅ 不依赖API提供的时间戳

#### 缺点
- ❌ 仍需获取所有文档内容（1597次请求）
- ❌ 检测阶段就需要3-5分钟
- ❌ 没有实际节省多少时间
- ❌ 存储和维护哈希表的开销

#### 适用场景
- 需要精确判断文档是否变化
- 变化率很低（<5%）
- 可以接受检测的时间成本

---

### 方案C：智能全量更新（推荐）⭐⭐⭐

#### 实现思路

```python
class SmartUpdater:
    def should_full_update(self) -> bool:
        """判断是否需要全量更新"""
        if not self.last_update_file.exists():
            return True

        last_time = datetime.fromisoformat(self._load_last_update()['timestamp'])

        # 超过7天，强制全量更新
        return datetime.now() - last_time > timedelta(days=7)

    def update(self, mode='auto'):
        """智能更新"""
        if mode == 'auto':
            if self.should_full_update():
                print("📅 距离上次更新已超过7天，执行全量更新")
                mode = 'full'
            else:
                print("🔄 快速检查文档数量...")
                mode = 'quick_check'

        if mode == 'full':
            return self._full_update()
        else:
            return self._quick_check_update()

    def _quick_check_update(self):
        """快速检查是否有变化"""
        # 只获取节点列表，对比数量
        nodes = learner.get_all_nodes(use_cache=False)
        old_metadata = self._load_metadata()

        old_count = old_metadata.get('total_docs', 0)
        new_count = len(nodes)

        if new_count == old_count:
            print(f"✅ 文档数量未变化 ({new_count} 个)")
            return True

        print(f"📊 文档数量变化: {old_count} → {new_count} ({new_count-old_count:+d})")

        # 有变化，执行全量更新
        return self._full_update()

    def _full_update(self):
        """全量更新（利用断点续传）"""
        # 运行完整学习（自动跳过已下载的文档）
        os.system("python3 learn_full_kb.py --auto")

        # 重建索引
        os.system("python3 build_full_kb_index.py")

        # 记录更新时间
        self._save_update_time()

        return True
```

#### 优点
- ✅ 实现简单，利用现有代码
- ✅ 断点续传保证可靠性
- ✅ 索引总是完整准确的
- ✅ 维护成本低
- ✅ 快速检查机制减少不必要的更新

#### 缺点
- ❌ 有变化时仍需10-30分钟
- ❌ 可能下载部分未变化的文档

#### 适用场景
- 周更新或更低频率
- 知识库规模适中（<5000文档）
- 优先保证准确性和可靠性

---

## 🎯 推荐方案：方案C（智能全量更新）

### 选择理由

1. **简单 > 复杂**：利用现有的断点续传机制
2. **可靠 > 高效**：保证索引100%准确
3. **维护成本低**：代码量少，易于调试
4. **周更新场景适用**：10-30分钟/周 = 1.4-4.3分钟/天

### 实施方案

#### 1. 创建统一更新脚本

```bash
# update_kb.py
python3 update_kb.py          # 智能判断
python3 update_kb.py --full   # 强制全量
```

#### 2. 集成到OpenClaw Skill

```python
# skill_main.py
def update(self, mode='auto'):
    result = subprocess.run(
        ['python3', 'update_kb.py', '--mode', mode],
        cwd=self.skill_dir,
        timeout=1800  # 30分钟超时
    )
    return result.returncode == 0
```

#### 3. 设置定时任务

```bash
# crontab -e
# 每周日凌晨2点全量更新
0 2 * * 0 cd /path/to/feishu-kb && python3 update_kb.py --full >> logs/update.log 2>&1

# 或：每天智能检查
0 2 * * * cd /path/to/feishu-kb && python3 update_kb.py >> logs/update.log 2>&1
```

## 📊 性能评估

### 时间成本

| 操作 | 时间 | 说明 |
|------|------|------|
| 快速检查 | ~5秒 | 只获取节点列表 |
| 全量更新 | 10-30分钟 | 下载1597个文档 + 重建索引 |
| 每周平均 | ~2-4分钟/天 | 分摊到每天 |

### 网络请求

| 操作 | 请求数 | 说明 |
|------|--------|------|
| 快速检查 | ~30个 | 分页获取节点列表 |
| 全量更新 | ~1600个 | 每个文档1次请求 |

## 🔮 未来优化方向

如果未来知识库规模扩大（>5000文档），可以考虑：

### 1. 分区更新

```python
# 按文档类别分区
categories = ['产品文档', '技术文档', '业务流程']

for category in categories:
    update_category(category, incremental=True)
```

### 2. 真正的增量索引

使用支持增量更新的向量数据库：
- Faiss (Facebook AI Similarity Search)
- Milvus
- Weaviate

### 3. 变更通知机制

如果飞书提供Webhook：
```python
@app.route('/webhook/feishu', methods=['POST'])
def feishu_webhook():
    # 接收文档变更通知
    # 只更新变化的文档
    pass
```

## 📝 总结

对于当前场景（1597文档 + 周更新），**方案C（智能全量更新）**是最佳选择：

- ✅ 简单可靠
- ✅ 维护成本低
- ✅ 时间成本可接受（10-30分钟/周）
- ✅ 利用现有代码（断点续传）

**核心理念：在合理的时间成本下，选择最简单可靠的方案。**

---

**文档版本**: v1.0
**创建日期**: 2026-03-08
**作者**: Claude Code
