# ⚠️ 当前限制：图片信息丢失问题

## 问题说明

**你的观察非常准确！** 当前的 `feishu-kb` skill 确实**只学习了文本信息，丢失了图片等视觉内容**。

## 📊 数据统计

### 图片引用数量
- **海外业务文档**: 10+ 个图片引用
- **完整知识库**: 3,890+ 个图片引用
- **总计**: 约 **3,900 个图片信息丢失**

### 示例

在 `overseas_content.txt` 中，我们可以看到：

```
产品研发模式示意

墨西哥-MUWE
墨西哥业务拓展策略与研发支持需求说明 1.0.pptx  墨西哥-MUWE（摘录）


image.png            ← 只保留了文件名


image.png            ← 没有实际图片内容

新加坡-AiMT Horizon
```

以及：
```
商家APP

合作伙伴

现状

计划

Beez

img_v3_02ss_0ed60f7f-8b6f-4bfd-a92d-170249f5ce0g.png    ← 只有引用标记
```

## 🔍 问题原因

### 当前实现方式

1. **使用 API**: `RawContentDocumentRequest`
   ```python
   request = RawContentDocumentRequest.builder() \
       .document_id(doc_id) \
       .lang(0) \
       .build()

   response = self.client.docx.v1.document.raw_content(request)
   content = response.data.content  # 只返回纯文本
   ```

2. **保存格式**: 纯文本 `.txt` 文件
   - 只保存文字内容
   - 图片只保留文件名引用（如 `image.png`）
   - 无法访问实际图片数据

### 丢失的信息类型

❌ **图片**（流程图、架构图、截图等）
❌ **表格**（可能只保留了文本内容，但丢失了表格结构）
❌ **附件**（PDF、Excel 等）
❌ **富文本格式**（颜色、字体、布局等）

## 🎯 影响分析

### 严重影响的场景

1. **产品架构图**
   - 例如：海外业务文档中的"产品研发模式示意图"
   - 无法理解系统架构关系

2. **流程图**
   - 例如：业务开通流程、支付流程图
   - 无法准确描述步骤顺序

3. **UI 截图**
   - 例如：商家 APP 界面截图
   - 无法了解实际界面布局

4. **数据表格**
   - 例如：多国本地化对比表格
   - 可能丢失了表格的结构化信息

5. **技术架构图**
   - 例如：CI/CD 工具链架构图
   - 无法理解技术体系

### 中等影响的场景

- 产品对比（有图片辅助说明）
- 操作步骤（有截图示意）
- 数据报表（图表可视化）

### 轻微影响的场景

- 纯文字描述的内容
- 已有文字说明的配置参数
- 文字型业务流程说明

## 💡 可能的解决方案

### 方案 1: 下载图片并使用 Claude 的多模态能力

**优点**:
- Claude 支持图片输入，可以"看懂"图片内容
- 可以理解架构图、流程图、截图等
- 最完整的信息保留

**实现思路**:
```python
# 1. 获取文档的完整结构（包括图片 token）
from lark_oapi.api.docx.v1 import GetDocumentRequest

response = client.docx.v1.document.get(GetDocumentRequest.builder()
    .document_id(doc_id)
    .build())

# 2. 遍历文档块，识别图片块
for block in response.data.document.body.blocks:
    if block.block_type == 'image':
        image_token = block.image.token

        # 3. 下载图片
        image_response = client.drive.v1.media.download(
            MediaDownloadRequest.builder()
            .file_token(image_token)
            .build())

        # 4. 保存图片
        with open(f'images/{image_token}.png', 'wb') as f:
            f.write(image_response.content)

# 5. 在检索时，将相关图片一起提供给 Claude
```

**挑战**:
- 需要下载和存储大量图片文件
- 存储空间增加（可能从 16MB 增加到 100MB+）
- 检索时需要处理图片数据
- API 调用次数增加

### 方案 2: 提取图片中的文字（OCR）

**优点**:
- 可以提取图片中的文字信息
- 仍然是纯文本索引，不增加太多复杂度
- 适合包含文字的图片（如表格截图、流程图等）

**实现思路**:
```python
# 使用飞书的 OCR API 或第三方 OCR
from lark_oapi.api.optical_char_recognition.v1 import *

# 下载图片后进行 OCR
response = client.optical_char_recognition.v1.image.basic_recognize(
    ImageBasicRecognizeRequest.builder()
    .image(image_data)
    .build())

text = response.data.text_list
# 将提取的文字追加到文档内容中
```

**挑战**:
- 对纯图形的架构图、流程图效果不好
- OCR 可能不准确
- 仍然丢失了视觉布局信息

### 方案 3: 保留图片链接，检索时动态获取

**优点**:
- 不增加存储空间
- 实现相对简单
- 保持纯文本检索的效率

**实现思路**:
```python
# 在文档内容中保留图片的完整信息
content_with_images = f"""
...文本内容...

[图片: {image_token}]
链接: https://sqb.feishu.cn/space/api/box/stream/download/...
位置: 产品架构图
上下文: 该图展示了海外业务产品研发模式

...继续文本内容...
"""

# 当用户查询时，如果匹配到包含图片的段落
# 可以在返回结果中提示："此段落包含图片，请查看原文档"
# 并提供图片链接
```

**挑战**:
- 无法真正"理解"图片内容
- 只是提供了查看途径
- 需要手动点击链接查看

### 方案 4: 生成图片描述（AI 辅助）

**优点**:
- 可以用文字描述图片内容
- 保持纯文本检索
- 补充图片的语义信息

**实现思路**:
```python
# 1. 下载图片
# 2. 使用 Claude API 生成图片描述
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-4-sonnet-20250514",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": base64_image,
                }
            },
            {
                "type": "text",
                "text": "请描述这张图片的内容，包括：1) 图片类型（架构图/流程图/截图等）2) 主要内容 3) 关键信息点"
            }
        ]
    }]
)

# 3. 将描述追加到文档内容中
description = response.content[0].text
content_with_desc = f"""
...文本内容...

[图片描述]
类型: 架构图
内容: {description}

...继续文本内容...
"""
```

**优点**:
- 可检索的文字信息
- 不需要在查询时处理图片
- 补充了图片的语义

**挑战**:
- 需要 API 调用（成本）
- 描述可能不够准确
- 处理时间较长（3900+ 图片）

## 🎯 推荐方案

### 短期方案（立即可行）

**方案 3 的增强版**: 保留图片元信息 + 手动标注重要图片

1. 在重新获取文档时，记录图片位置和上下文
2. 对关键图片（架构图、流程图）手动添加描述
3. 在检索结果中提示包含图片

**实现优先级**:
```python
# 1. 修改 fetch 脚本，保留图片 token
# 2. 在文本中标记图片位置
# 3. 手动为TOP 50 重要图片添加描述
```

### 中期方案（1-2周）

**方案 4**: AI 辅助生成图片描述

1. 下载所有图片
2. 使用 Claude API 批量生成描述
3. 将描述整合到文本中
4. 重新构建索引

**成本估算**:
- 3,900 张图片 × 约 $0.002/图 = $7.8
- 可以分批处理

### 长期方案（未来优化）

**方案 1**: 完整的多模态检索

1. 下载并保存所有图片
2. 构建支持图片的检索系统
3. 查询时同时检索文本和图片
4. 使用 Claude 的多模态能力理解图片

## 📋 行动建议

### 立即可做

1. **在文档中标注图片信息**
   ```
   在 SKILL.md 中添加：
   ⚠️ 当前版本仅包含文本内容，约3,900张图片暂未处理
   如需查看图片，请访问原始飞书文档
   ```

2. **优化检索结果显示**
   ```python
   # 如果检索到的内容包含 "image.png" 等标记
   # 在结果中提示："此段落包含图表，建议查看原文档获取完整信息"
   ```

3. **创建重要图片清单**
   ```
   手动列出最重要的图片：
   - 海外业务产品架构图
   - 聚合点单业务流程图
   - 技术架构示意图
   - 等等

   为这些图片添加详细的文字描述
   ```

### 后续改进

如果你认为图片信息很重要，我可以帮你：

1. 实现图片下载功能
2. 使用 Claude API 批量生成图片描述
3. 重新构建包含图片描述的知识库
4. 或者实现完整的多模态检索系统

## 📞 你的选择

请告诉我你希望如何处理这个问题：

- **A**: 接受现状，仅使用文本信息（最快）
- **B**: 添加重要图片的手动描述（中等工作量）
- **C**: 使用 AI 生成所有图片描述（需要 API 成本）
- **D**: 实现完整的多模态系统（长期项目）

---

**当前状态**: ⚠️ 已识别图片丢失问题
**影响**: 约 3,900 张图片信息未被索引
**紧急程度**: 中等（取决于图片对业务理解的重要性）
