# 🚀 OpenClaw Skill 部署完成

## ✅ 部署状态

**Skill 已成功部署到 OpenClaw！**

- **位置**: `~/.claude/plugins/marketplaces/custom-skills/feishu-kb`
- **类型**: 符号链接
- **版本**: v1.1.0
- **状态**: ✅ 激活

## 📍 文件结构

```
~/.claude/plugins/marketplaces/custom-skills/
└── feishu-kb -> /Users/macuser/Desktop/Start/Skills/Feishu PKB
    ├── plugin.json          (新增 - OpenClaw插件配置)
    ├── skill.json           (Skill元数据)
    ├── _meta.json           (版本信息)
    ├── SKILL.md             (完整文档)
    ├── skill_main.py        (入口文件)
    ├── data/                (离线知识库)
    │   ├── vectors.npz
    │   ├── bm25_index.pkl
    │   ├── kb_data.db
    │   └── ...
    └── src/                 (源代码)
```

## 🎯 如何使用

### 在 Claude Code 中使用

在任何 Claude Code 会话中，你都可以使用以下命令：

```bash
# 搜索国内业务
/feishu-kb search 扫码王

# 搜索海外业务
/feishu-kb search 马来西亚Beez
/feishu-kb search 墨西哥MUWE
/feishu-kb search 聚合点单

# 查看知识库状态
/feishu-kb status

# 更新知识库
/feishu-kb update
```

### 直接调用

你也可以直接运行 Python 脚本：

```bash
cd "/Users/macuser/Desktop/Start/Skills/Feishu PKB"

# 搜索
python3 skill_main.py search "查询内容"

# 查看状态
python3 skill_main.py status

# 更新索引
python3 skill_main.py update
```

## 📊 知识库信息

### 版本 v1.1.0 (2026-03-08)

- **文档总数**: 1,597+ (国内1597 + 海外1)
- **文档块数**: 7,507
- **总字符数**: 3,112,389 (约311万字符)
- **向量维度**: 768
- **覆盖区域**: 中国 + 马来西亚 + 墨西哥 + 越南 + 新加坡

### 支持的业务查询

**国内业务：**
- 扫码王、收钱音箱、智能POS
- 支付通道、结算、交易
- 商户管理、进件流程
- CRM、SPA、OMS系统

**海外业务：**
- 🇲🇾 马来西亚Beez：扫码点单、收银POS、分账、本地钱包
- 🇲🇽 墨西哥MUWE：收银系统、Apple Pay、三方外卖
- 🇻🇳 越南LitPay：动态码支付、Napas对接
- 🇸🇬 新加坡AiMT：UQPay/YeahPay进件、POS机软件

## 🔄 更新 Skill

当知识库有新内容时，只需重新构建索引：

```bash
cd "/Users/macuser/Desktop/Start/Skills/Feishu PKB"

# 1. 获取新文档（如果有）
python3 learn_full_kb.py --auto

# 2. 重新构建索引
python3 build_full_kb_index.py

# 3. 验证
python3 verify_system.py
```

由于使用的是符号链接，更新会自动生效到 OpenClaw。

## 🛠️ 维护

### 查看 Skill 链接状态
```bash
ls -la ~/.claude/plugins/marketplaces/custom-skills/
```

### 重新创建链接（如果需要）
```bash
cd ~/.claude/plugins/marketplaces/custom-skills
rm -f feishu-kb
ln -s "/Users/macuser/Desktop/Start/Skills/Feishu PKB" feishu-kb
```

### 移除 Skill
```bash
rm ~/.claude/plugins/marketplaces/custom-skills/feishu-kb
```

## 📝 配置文件

### plugin.json
插件系统的配置文件，定义了 skill 的基本信息和命令。

### skill.json
Skill 的详细配置，包括命令参数、环境变量等。

### _meta.json
简化的元数据文件，用于快速识别版本。

## ✅ 验证部署

运行以下命令验证 skill 是否正常工作：

```bash
# 方法1: 使用命令行
python3 "/Users/macuser/Desktop/Start/Skills/Feishu PKB/skill_main.py" search "扫码王"

# 方法2: 在新的 Claude 会话中
# 输入: /feishu-kb search 扫码王
```

## 📚 相关文档

- [SKILL.md](./SKILL.md) - 完整的 Skill 使用文档
- [UPDATE_LOG_v1.1.0.md](./UPDATE_LOG_v1.1.0.md) - v1.1.0 更新日志
- [QUICKSTART_OPENCLAW.md](./QUICKSTART_OPENCLAW.md) - 快速开始指南
- [README.md](./README.md) - 项目主文档

## 🎉 部署完成

Skill 已成功部署到 OpenClaw 并可以使用！

你现在可以在任何 Claude Code 会话中使用 `/feishu-kb` 命令来搜索收钱吧的国内和海外业务知识。

---

**最后更新**: 2026-03-08
**版本**: v1.1.0
**部署位置**: `~/.claude/plugins/marketplaces/custom-skills/feishu-kb`
