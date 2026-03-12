# 🚀 OpenClaw Skill 快速开始

## ✅ 系统已就绪

你的飞书离线知识库已经配置为OpenClaw Skill，可以立即使用！

---

## 📝 使用方法

### 1. 搜索知识库（最常用）

```bash
# 在OpenClaw中使用
/feishu-kb search 扫码王

# 或直接运行
python3 skill_main.py search 扫码王
```

**输出示例：**
```
✅ 飞书知识库已加载

📚 查询: 扫码王
模式: hybrid
结果数: 5
======================================================================

1. 【分数: 0.033】
   标题: 收钱吧产品知识库
   内容: 3电饱饱业务
          电饱饱B端小程序
          14终端业务
          1. 扫码王
          常见问题处理
          扫码王III代
          扫码王IV代...

2. 【分数: 0.032】
   标题: 收钱吧产品知识库
   内容: 分润项导入
          收款对账系统...
```

### 2. 查看知识库状态

```bash
/feishu-kb status

# 或
python3 skill_main.py status
```

**输出示例：**
```
📊 知识库状态
======================================================================
构建时间: 2026-03-07 13:35:52
文档块数: 10
向量维度: 768
模型: moka-ai/m3e-base or TF-IDF

文件大小:
  vectors: 2.1 KB
  bm25: 23.2 KB
  database: 32.0 KB
  content: 14.2 KB

搜索引擎: loaded
```

### 3. 更新知识库

```bash
/feishu-kb update

# 或
python3 skill_main.py update
```

这会：
1. 从飞书获取最新内容
2. 重新构建索引
3. 重新加载搜索引擎

---

## 🎯 常用命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `search <查询>` | 搜索知识库 | `/feishu-kb search 扫码王` |
| `status` | 查看状态 | `/feishu-kb status` |
| `update` | 更新知识库 | `/feishu-kb update` |

### 高级参数

```bash
# 指定检索模式
/feishu-kb search 扫码王 --mode vector    # 仅向量检索
/feishu-kb search 扫码王 --mode keyword   # 仅关键词检索
/feishu-kb search 扫码王 --mode hybrid    # 混合检索（默认）

# 指定返回数量
/feishu-kb search 扫码王 --top-k 10       # 返回10个结果

# JSON格式输出
/feishu-kb search 扫码王 --format json    # 便于程序处理
```

---

## 📦 OpenClaw集成

### 方式1: 本地Skill

如果你的Skill目录在OpenClaw可访问的位置：

```bash
# Skill已在此目录：
/Users/macuser/Desktop/Start/Skills/Feishu PKB

# 可以直接使用 /feishu-kb 命令
```

### 方式2: 安装到OpenClaw

```bash
# 如果OpenClaw支持skill安装
openclaw skill install "/Users/macuser/Desktop/Start/Skills/Feishu PKB"

# 查看已安装的skills
openclaw skill list

# 查看skill详情
openclaw skill info feishu-kb
```

### 方式3: 创建符号链接

```bash
# 链接到OpenClaw的skills目录
ln -s "/Users/macuser/Desktop/Start/Skills/Feishu PKB" ~/.openclaw/skills/feishu-kb

# 然后就可以使用
/feishu-kb search 扫码王
```

---

## 🧪 测试Skill

### 测试1: 基本搜索

```bash
cd "/Users/macuser/Desktop/Start/Skills/Feishu PKB"
python3 skill_main.py search 扫码王
```

**预期输出：** 返回3-5个相关结果

### 测试2: 不同检索模式

```bash
# 向量检索
python3 skill_main.py search 产品白皮书 --mode vector

# 关键词检索
python3 skill_main.py search 收钱吧APP --mode keyword

# 混合检索
python3 skill_main.py search 支付业务 --mode hybrid
```

### 测试3: 状态检查

```bash
python3 skill_main.py status
```

**预期输出：** 显示知识库元数据和文件大小

---

## 💡 实际使用场景

### 场景1: 客服查询

```bash
# 客户询问扫码王相关问题
/feishu-kb search 扫码王有哪些型号

# 查询产品功能
/feishu-kb search 收钱吧APP支持哪些功能

# 查找操作指南
/feishu-kb search 如何开通支付业务
```

### 场景2: 产品培训

```bash
# 了解产品结构
/feishu-kb search 产品白皮书

# 查询业务流程
/feishu-kb search 进件流程

# 学习系统模块
/feishu-kb search CRM系统功能
```

### 场景3: 技术支持

```bash
# 查找技术文档
/feishu-kb search API接口说明

# 问题诊断
/feishu-kb search 常见问题处理

# 系统配置
/feishu-kb search 系统参数设置
```

---

## 🔧 配置与定制

### 调整检索参数

编辑 `config/config.yaml`：

```yaml
retrieval:
  vector_search:
    top_k: 10                    # 默认返回数量
    similarity_threshold: 0.7     # 相似度阈值

  keyword_search:
    top_k: 10

  hybrid:
    vector_weight: 0.5           # 向量检索权重
    keyword_weight: 0.5          # 关键词检索权重
```

### 自定义分块策略

编辑 `config/config.yaml`：

```yaml
indexing:
  chunking:
    strategy: recursive          # 分块策略
    chunk_size: 512             # 块大小
    chunk_overlap: 50           # 重叠大小
```

---

## 📊 性能说明

| 指标 | 数值 | 说明 |
|------|------|------|
| **首次加载** | ~2秒 | 加载索引和模型 |
| **后续查询** | <100ms | 纯内存计算 |
| **内存占用** | ~200MB | 运行时内存 |
| **存储空间** | <100KB | 索引文件总大小 |

---

## 🔄 维护任务

### 定期更新知识库

```bash
# 每天/每周运行一次
/feishu-kb update

# 或设置定时任务（crontab）
0 2 * * * cd "/Users/macuser/Desktop/Start/Skills/Feishu PKB" && python3 skill_main.py update
```

### 监控Skill健康

```bash
# 检查状态
/feishu-kb status

# 完整系统验证
python3 verify_system.py
```

### 问题诊断

```bash
# 如果搜索无结果
python3 skill_main.py status          # 检查索引
python3 verify_system.py              # 验证系统
python3 skill_main.py update          # 重建索引

# 如果更新失败
python3 fetch_wiki_content.py        # 单独测试数据获取
python3 build_offline_kb_fast.py     # 单独测试索引构建
```

---

## 📚 更多文档

- [OPENCLAW_SKILL_GUIDE.md](OPENCLAW_SKILL_GUIDE.md) - 完整Skill部署指南
- [README.md](README.md) - 项目主文档
- [README_USAGE.md](README_USAGE.md) - 详细使用说明
- [SYSTEM_STATUS.md](SYSTEM_STATUS.md) - 系统状态报告

---

## 🎊 开始使用

```bash
# 测试搜索
python3 skill_main.py search 扫码王

# 查看状态
python3 skill_main.py status

# 在OpenClaw中使用
/feishu-kb search 你的查询
```

---

**✨ 你的飞书知识库Skill已就绪！开始查询吧！**

常用命令速查：
- 搜索：`/feishu-kb search <查询>`
- 状态：`/feishu-kb status`
- 更新：`/feishu-kb update`
