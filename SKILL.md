---
name: feishu-kb
description: 收钱吧产品专家 - 解答产品问题、产品咨询、功能查询。涵盖国内+海外全业务产品知识（扫码王、聚合支付、Beez、MUWE、LitPay等），支持图片内容理解
homepage: https://sqb.feishu.cn
metadata: {"clawdbot":{"emoji":"📚","requires":{"bins":["python3"],"env":["FEISHU_APP_ID","FEISHU_APP_SECRET"]},"primaryEnv":"FEISHU_APP_ID"}}
---

# 收钱吧产品专家（飞书知识库）

收钱吧产品知识库智能检索系统，提供产品咨询、功能查询、技术方案等全方位产品问题解答。

## 覆盖范围

- **国内业务**：扫码王、收钱吧APP、聚合支付、分账清结算等
- **海外业务**：马来西亚Beez、墨西哥MUWE、越南LitPay、新加坡等
- **产品文档**：产品白皮书、技术方案、业务规划等

## 使用方法

### 搜索产品知识

```bash
python3 {baseDir}/skill_main.py search "查询内容"
python3 {baseDir}/skill_main.py search "扫码王功能" --top-k 5
python3 {baseDir}/skill_main.py search "海外业务" --mode hybrid
```

### 学习单个文档（增量更新）⭐新功能

```bash
# 通过文档URL学习
python3 {baseDir}/skill_main.py learn "https://xxx.feishu.cn/docx/xxxxx"

# 通过文档ID学习
python3 {baseDir}/skill_main.py learn "doxcnxxxxxx"
```

### 查看知识库状态

```bash
python3 {baseDir}/skill_main.py status
```

### 更新知识库索引（全量更新）

```bash
python3 {baseDir}/skill_main.py update
```

## 搜索选项

- `--top-k <N>`: 返回结果数量（默认：5）
- `--mode <mode>`: 搜索模式
  - `hybrid`: 混合搜索（默认，语义+关键词）
  - `vector`: 纯语义搜索
  - `keyword`: 纯关键词搜索
- `--with-images`: 启用图片内容检测（默认开启）
- `--no-images`: 禁用图片检测

## 功能特性

- ✅ **智能检索**：TF-IDF向量搜索 + BM25关键词搜索 + RRF融合
- ✅ **图片理解**：自动检测并标注文档中的图片内容
- ✅ **离线访问**：本地索引，无需实时访问飞书
- ✅ **中文优化**：jieba分词，针对中文优化

## 环境要求

需要配置以下环境变量：
- `FEISHU_APP_ID`: 飞书应用ID
- `FEISHU_APP_SECRET`: 飞书应用Secret
- `ANTHROPIC_API_KEY`: Claude API密钥（图片理解功能，可选）

## 知识库统计

- 文档块数：7507+
- 向量维度：768
- 图片数量：14580+
- 覆盖内容：3.1M+ 字符
