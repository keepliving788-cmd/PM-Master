# 🌱 可持续的图片内容学习方案

## 问题回顾

你提出的关键问题：
1. **成本**: $48/次，知识库持续更新会累积
2. **维护**: 每次更新都要重新处理，不可持续

## 💡 更好的方案

### 方案 1: 飞书 MCP + 实时查询 ⭐ 推荐

**原理**: 不提前处理图片，而是在查询时实时获取

#### 工作流程

```
用户查询 "商户进件流程"
    ↓
检索到相关文档段落
    ↓
发现段落包含图片引用
    ↓
通过飞书 MCP 实时获取该图片
    ↓
调用 Claude API "看"图片
    ↓
返回：文本 + 图片内容理解
```

#### 优势

✅ **零前期成本** - 不需要提前处理 14,580 张图片
✅ **按需付费** - 只为实际查询到的图片付费
✅ **自动更新** - 知识库更新时无需重新处理图片
✅ **成本可控** - 假设每次查询平均涉及 2 张图片：
   - 每次查询成本: ~$0.006 (2张图片)
   - 100次查询: ~$0.6
   - 比批量处理便宜得多！

#### 实现方式

你的 settings.json 已经配置了飞书 MCP：

```json
{
  "mcpServers": {
    "feishu-mcp": {
      "url": "https://open.feishu.cn/mcp/stream/..."
    }
  }
}
```

我可以利用这个：

```python
# skill_main.py 中添加实时图片理解

def search_with_images(query: str):
    # 1. 常规文本检索
    results = search_engine.search(query, mode='hybrid')

    # 2. 检查结果中是否包含图片引用
    for result in results:
        if has_image_reference(result):
            # 3. 通过飞书 MCP 获取图片
            images = fetch_images_via_mcp(result['doc_id'])

            # 4. 让 Claude "看"图片并理解内容
            image_content = understand_images(images)

            # 5. 增强返回结果
            result['content'] += f"\n\n[图片内容]: {image_content}"

    return results
```

#### 成本对比

| 场景 | 方案 A（批量预处理） | 方案 1（实时查询）|
|------|---------------------|-----------------|
| 初始成本 | $48 | $0 |
| 每次查询 | $0 | ~$0.006 |
| 100次查询 | $0 | $0.6 |
| 知识库更新 | +$3-6 | $0 |
| 年度成本（10次更新，1000次查询）| $48 + $30-60 = $78-108 | $6 |

**节省**: 约 **$72-102/年** (92%+)

---

### 方案 2: 智能缓存 + 增量处理

**原理**: 只处理新增/修改的图片，已处理的缓存

#### 工作流程

```
首次运行:
├─ 处理所有图片 ($48)
└─ 保存图片描述缓存

后续更新:
├─ 检查哪些图片是新的
├─ 只处理新图片 (可能 $3-6)
└─ 更新缓存

查询时:
└─ 直接使用缓存的描述
```

#### 实现

```python
# 图片缓存数据库
{
  "image_token_123": {
    "description": "流程图展示...",
    "processed_at": "2026-03-08",
    "hash": "abc123..."
  }
}

# 增量处理逻辑
def process_new_images():
    all_images = get_all_image_tokens()
    cached = load_cache()

    new_images = [img for img in all_images if img not in cached]

    print(f"总图片: {len(all_images)}")
    print(f"已缓存: {len(cached)}")
    print(f"需处理: {len(new_images)}")  # 通常很少

    # 只处理新图片
    for img in new_images:
        desc = process_image_with_claude(img)
        cached[img] = desc

    save_cache(cached)
```

#### 优势

✅ **首次成本**: $48（一次性）
✅ **后续更新**: 只需 $1-5（增量）
✅ **查询快速**: 使用缓存，无API调用

#### 劣势

❌ 仍需首次投入 $48
❌ 需要维护缓存数据库

---

### 方案 3: 分批次处理 + 优先级

**原理**: 不一次性处理所有图片，按重要性分批

#### 策略

```
批次 1 (高优先级 - 立即处理):
- 架构图、流程图
- 产品对比图
- 操作步骤图
估计: 500-1000 张 → $3-6

批次 2 (中优先级 - 1周后):
- 功能截图
- 数据报表
估计: 2000-3000 张 → $12-18

批次 3 (低优先级 - 按需):
- 装饰性图片
- 重复性图片
估计: 剩余图片 → 暂不处理
```

#### 识别优先级

```python
def classify_image_priority(context: str) -> str:
    """根据图片上下文判断优先级"""
    high_keywords = ['架构', '流程', '步骤', '对比', '模式']
    mid_keywords = ['功能', '界面', '示例', '数据']

    for keyword in high_keywords:
        if keyword in context:
            return 'HIGH'

    for keyword in mid_keywords:
        if keyword in context:
            return 'MEDIUM'

    return 'LOW'
```

#### 优势

✅ **分散成本**: 不一次性投入 $48
✅ **快速见效**: 重要图片先处理
✅ **灵活控制**: 可随时停止

---

### 方案 4: 使用开源多模态模型（本地）

**原理**: 使用本地运行的开源模型处理图片

#### 可选模型

- **LLaVA**: 开源视觉语言模型
- **MiniCPM-V**: 轻量级多模态
- **Qwen-VL**: 阿里开源

#### 成本

- 初始: 下载模型（~4GB）
- 运行: 本地GPU/CPU（免费）
- 优点: 无API成本
- 缺点: 效果不如 Claude，需要本地计算资源

---

## 🎯 综合推荐

### 立即实施：方案 1（实时查询）⭐⭐⭐⭐⭐

**理由**:
1. **零初始成本**
2. **按实际使用付费**（每次查询 $0.006）
3. **自动适配更新**（无需维护）
4. **最灵活**

**实施步骤**:

```python
# 第1步: 修改 skill_main.py
class SearchWithImages:
    def __init__(self):
        self.search_engine = SimpleSearchEngine()
        self.feishu_client = setup_feishu_mcp()

    def search(self, query, include_images=True):
        # 文本检索
        results = self.search_engine.search(query)

        if not include_images:
            return results

        # 实时获取并理解图片
        for result in results:
            if self._has_images(result):
                result = self._enrich_with_images(result)

        return results

    def _enrich_with_images(self, result):
        # 通过飞书 MCP 获取图片
        images = self.feishu_client.get_images(result['doc_token'])

        # 使用 Claude 理解图片（实时调用）
        for img in images:
            desc = self._understand_image(img)
            result['content'] += f"\n[图片]: {desc}"

        return result
```

**成本预估**:
- 假设每月 100 次查询
- 平均每次涉及 2 张图片
- 月成本: 100 × 2 × $0.003 = $0.6
- **年成本: ~$7** (vs 批量预处理的 $78-108)

### 备选：方案 2（智能缓存）⭐⭐⭐⭐

如果你希望查询速度绝对快（不能有API延迟），可以用这个：
- 首次投入 $48
- 后续增量更新只需 $1-5
- 查询零成本（使用缓存）

### 临时方案：方案 3（分批处理）⭐⭐⭐

如果想快速改善体验：
- 先处理 500 张重要图片（$3-6）
- 1-2周内见效
- 后续按需扩展

---

## 📋 决策建议

### 如果你在意成本 → 方案 1（实时）
- 最低总成本
- 按需付费
- 自动适配更新

### 如果你在意速度 → 方案 2（缓存）
- 查询无延迟
- 首次投入后长期零成本

### 如果你想快速试验 → 方案 3（分批）
- 低初始投入
- 快速看到效果
- 灵活可控

---

## 💬 我的强烈推荐

**方案 1（实时查询）**

因为：
1. 你提到"后续知识库会不断更新" → 方案1完全自动适配
2. $7/年 vs $78-108/年 → 节省90%+
3. 实现简单，利用现有的飞书MCP
4. 用户体验好（实时获取最新图片）

唯一的"成本"是查询时有 1-2 秒的图片处理延迟，但这是值得的。

---

## 🤔 你的选择

请告诉我：

**A. 方案 1** - 实时查询（推荐）
   - 成本: ~$7/年
   - 优点: 自动更新，最省钱
   - 缺点: 查询有轻微延迟

**B. 方案 2** - 智能缓存
   - 成本: $48首次 + $5-10/年
   - 优点: 查询快速，无延迟
   - 缺点: 需要首次投入

**C. 方案 3** - 分批处理
   - 成本: $3-6 先启动
   - 优点: 快速见效，可控
   - 缺点: 仍需逐步投入

**D. 暂时不处理**
   - 继续使用纯文本版本
   - 等待更好的方案

或者你有其他想法？
