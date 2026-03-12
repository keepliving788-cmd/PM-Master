# 🚀 OpenClaw Skill 部署指南

## 📋 概述

本项目已配置为OpenClaw Skill，可以作为独立技能部署到OpenClaw系统中。

---

## 🎯 Skill功能

### 命令列表

1. **搜索知识库**
   ```bash
   /feishu-kb search <查询内容>
   ```

2. **更新知识库**
   ```bash
   /feishu-kb update
   ```

3. **查看状态**
   ```bash
   /feishu-kb status
   ```

---

## 📦 部署步骤

### 1. 准备环境

```bash
# 确保Python 3.8+已安装
python3 --version

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置飞书凭证

创建 `.env` 文件（或复制 `.env.example`）：

```bash
cp .env.example .env
```

编辑 `.env`，填写飞书应用凭证：

```bash
FEISHU_APP_ID=你的应用ID
FEISHU_APP_SECRET=你的应用SECRET
FEISHU_WIKI_SPACE_ID=知识库空间ID
FEISHU_WIKI_TOKEN=N9kgwANVwifcisk9UT6cDOFInRe
```

### 3. 初始化Skill

```bash
python3 setup_skill.py
```

这会检查：
- ✅ 配置文件
- ✅ Python依赖
- ✅ 知识库索引

### 4. 构建知识库索引

```bash
# 方式1: 使用Skill命令
python3 skill_main.py update

# 方式2: 手动构建
python3 fetch_wiki_content.py
python3 build_offline_kb_fast.py
```

### 5. 测试Skill

```bash
# 测试搜索
python3 skill_main.py search 扫码王

# 查看状态
python3 skill_main.py status
```

---

## 💡 使用示例

### 搜索知识库

```bash
# 基本搜索
/feishu-kb search 扫码王

# 指定检索模式
/feishu-kb search 收钱吧APP --mode hybrid

# 返回更多结果
/feishu-kb search 产品白皮书 --top-k 10

# JSON格式输出
/feishu-kb search 支付业务 --format json
```

**输出示例：**
```
📚 查询: 扫码王
模式: hybrid
结果数: 3
======================================================================

1. 【分数: 0.033】
   标题: 收钱吧产品知识库
   内容: 3电饱饱业务
电饱饱B端小程序
电饱饱CRM端
14终端业务
1. 扫码王
常见问题处理
扫码王III代
扫码王IV代...

2. 【分数: 0.032】
   标题: 收钱吧产品知识库
   内容: 单管理
分润项导入
收款对账系统...
```

### 更新知识库

```bash
/feishu-kb update
```

**输出示例：**
```
🔄 开始更新知识库...

[1/2] 从飞书获取内容...
✅ 内容获取成功

[2/2] 构建离线索引...
✅ 索引构建成功

✅ 知识库更新成功
```

### 查看状态

```bash
/feishu-kb status
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
  bm25: 23.8 KB
  database: 32.0 KB
  content: 14.5 KB

搜索引擎: loaded
```

---

## 🔧 OpenClaw集成

### skill.json配置

Skill元数据定义在 `skill.json`：

```json
{
  "name": "feishu-kb",
  "version": "1.0.0",
  "description": "飞书离线知识库检索",
  "type": "query",
  "entry": "skill_main.py",
  "commands": [
    {
      "name": "search",
      "description": "搜索知识库",
      "usage": "/feishu-kb search <查询内容>"
    }
  ]
}
```

### 作为OpenClaw Skill安装

如果你的OpenClaw支持skill安装，可以：

```bash
# 方式1: 从本地目录安装
openclaw skill install /path/to/Feishu\ PKB

# 方式2: 从Git仓库安装（如果你上传到Git）
openclaw skill install git+https://your-repo.git
```

---

## 📊 架构说明

```
用户命令
   ↓
skill_main.py (入口)
   ↓
┌─────────────────────────────────┐
│  FeishuKBSkill                  │
│  • search()   - 搜索知识库       │
│  • update()   - 更新索引         │
│  • status()   - 查看状态         │
└─────────────────────────────────┘
   ↓
SimpleSearchEngine (检索引擎)
   ↓
离线索引 (TF-IDF + BM25 + SQLite)
```

---

## 🎨 高级用法

### 1. 在Python代码中使用

```python
from skill_main import FeishuKBSkill

# 初始化
skill = FeishuKBSkill()

# 搜索
result = skill.search("扫码王", top_k=5, mode='hybrid')

# 更新
result = skill.update()

# 状态
result = skill.status()
```

### 2. 集成到其他系统

```python
import subprocess
import json

# 调用skill
result = subprocess.run(
    ['python3', 'skill_main.py', 'search', '扫码王', '--format', 'json'],
    capture_output=True,
    text=True
)

data = json.loads(result.stdout)
print(data['results'])
```

### 3. 自定义配置

编辑 `config/config.yaml` 调整检索参数：

```yaml
retrieval:
  vector_search:
    top_k: 10
    similarity_threshold: 0.7

  hybrid:
    vector_weight: 0.5
    keyword_weight: 0.5
```

---

## 🔄 维护与更新

### 定期更新知识库

```bash
# 设置定时任务（每天更新）
# 编辑 crontab
crontab -e

# 添加任务（每天凌晨2点）
0 2 * * * cd /path/to/Feishu\ PKB && python3 skill_main.py update
```

### 监控Skill状态

```bash
# 检查知识库状态
/feishu-kb status

# 验证系统
python3 verify_system.py
```

### 重新构建索引

```bash
# 如果数据损坏或需要完全重建
rm -rf data/*.npz data/*.pkl data/*.db
/feishu-kb update
```

---

## 🐛 故障排查

### 问题1: Skill初始化失败

```bash
# 检查依赖
pip install -r requirements.txt

# 重新初始化
python3 setup_skill.py
```

### 问题2: 搜索无结果

```bash
# 检查索引是否存在
/feishu-kb status

# 重新构建
/feishu-kb update
```

### 问题3: 飞书API错误

```bash
# 检查.env配置
cat .env

# 验证凭证
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print(f'APP_ID: {os.getenv(\"FEISHU_APP_ID\")}')"

# 测试API连接
python3 fetch_wiki_content.py
```

---

## 📚 相关文档

- [README.md](README.md) - 项目主文档
- [README_USAGE.md](README_USAGE.md) - 详细使用指南
- [SYSTEM_STATUS.md](SYSTEM_STATUS.md) - 系统状态
- [PROJECT_COMPLETE.md](PROJECT_COMPLETE.md) - 完工报告

---

## 🎯 快速开始清单

- [ ] 安装Python依赖: `pip install -r requirements.txt`
- [ ] 配置飞书凭证: 编辑 `.env`
- [ ] 初始化Skill: `python3 setup_skill.py`
- [ ] 构建索引: `/feishu-kb update`
- [ ] 测试搜索: `/feishu-kb search 扫码王`
- [ ] 查看状态: `/feishu-kb status`

---

## 🎉 开始使用

```bash
# 一键测试
python3 skill_main.py search 扫码王
```

---

**✨ 现在你的飞书知识库已作为OpenClaw Skill部署完成！**

使用 `/feishu-kb` 命令开始查询知识库。
