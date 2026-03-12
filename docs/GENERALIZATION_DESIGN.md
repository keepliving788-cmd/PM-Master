# 飞书知识库Skill通用化方案设计

## 📋 背景

当前系统是为特定的飞书知识库（1597个文档）构建的离线检索系统。为了发布到GitHub供其他用户使用，需要设计通用化方案，使其能够适配任意飞书知识库。

## 🎯 设计目标

1. **通用性**：支持任意飞书知识库
2. **易用性**：配置过程简单友好
3. **轻量级**：GitHub仓库不包含大型数据文件
4. **可维护性**：代码结构清晰，易于扩展

## 🔍 核心问题

### 问题1：数据存储策略

当前系统包含20MB的索引数据（`data/`目录），是否应该提交到Git？

#### 选项A：不包含数据（推荐）⭐

```
GitHub仓库：只包含代码
用户本地：自己生成索引数据
```

**优点：**
- ✅ 仓库轻量，克隆快速
- ✅ 适配任意知识库
- ✅ 数据实时最新
- ✅ 避免敏感信息泄露

**缺点：**
- ❌ 首次使用需要10-30分钟学习
- ❌ 需要用户配置飞书凭证
- ❌ 新用户无法快速体验

#### 选项B：包含示例数据

```
GitHub仓库：包含一个小型示例知识库的索引
用户选择：使用示例或配置自己的
```

**优点：**
- ✅ 新用户可以快速体验
- ✅ 有完整的示例参考

**缺点：**
- ❌ 仓库体积增大（20-50MB）
- ❌ 示例数据可能包含敏感信息
- ❌ 实际使用仍需重新配置

**结论：选择方案A（不包含数据）**

理由：
1. 每个用户的知识库不同，示例数据意义不大
2. GitHub仓库应保持轻量
3. 通过完善的初始化向导提升用户体验

---

### 问题2：初始化时机

什么时候让用户配置和生成索引？

#### 选项A：安装时（install hook）

```bash
# 用户克隆后
git clone https://github.com/user/feishu-kb-skill
cd feishu-kb-skill
./install.sh  # 自动运行初始化
```

**优点：**
- ✅ 安装即可用
- ✅ 流程统一

**缺点：**
- ❌ 安装过程可能很长（10-30分钟）
- ❌ 安装失败处理复杂
- ❌ 不适合OpenClaw自动安装

#### 选项B：首次使用时（推荐）⭐

```bash
# 用户安装后，首次调用时
python3 skill_main.py search "查询"
# → 检测到未初始化
# → 提示运行: python3 init_kb.py
# → 或自动启动向导
```

**优点：**
- ✅ 安装快速（只克隆代码）
- ✅ 用户有准备时间
- ✅ 可以先阅读文档
- ✅ 失败可以重试

**缺点：**
- ❌ 不是"开箱即用"
- ❌ 需要明确的提示信息

#### 选项C：手动初始化（最灵活）⭐⭐

```bash
# 用户明确知道需要初始化
git clone https://github.com/user/feishu-kb-skill
cd feishu-kb-skill
pip install -r requirements.txt
python3 init_kb.py  # 明确的初始化步骤
```

**优点：**
- ✅ 用户有完全控制权
- ✅ 流程清晰透明
- ✅ 适合技术用户
- ✅ 易于调试

**缺点：**
- ❌ 需要阅读文档
- ❌ 多一个步骤

**结论：选择方案C + 选项B的自动检测**

```python
# skill_main.py
def search(self, query, ...):
    if not self._check_initialized():
        print("⚠️  知识库未初始化")
        print()
        print("请运行初始化向导:")
        print("  python3 init_kb.py")
        print()
        print("或查看文档: README.md")
        return {'error': 'not_initialized'}
```

---

### 问题3：配置方式

如何让用户提供飞书凭证和知识库信息？

#### 当前实现：交互式向导（已有）

```python
# init_kb.py
def interactive_config():
    print("🚀 飞书离线知识库Skill - 初始化向导")

    # 步骤1: 输入飞书凭证
    app_id = input("FEISHU_APP_ID: ")
    app_secret = getpass("FEISHU_APP_SECRET (输入不可见): ")

    # 步骤2: 输入知识库信息（支持3种方式）
    wiki_input = input("知识库URL/Space ID/Wiki Token: ")

    # 步骤3: 验证配置
    verify_config()

    # 步骤4: 学习知识库
    start_learning()
```

**支持的输入方式：**
```python
# 方式1: 飞书URL
https://xxx.feishu.cn/wiki/N9kgwANVwi...

# 方式2: Space ID
7480754861085147139

# 方式3: Wiki Token
N9kgwANVwi...
```

**优点：**
- ✅ 用户体验好
- ✅ 支持多种输入方式
- ✅ 即时验证
- ✅ 提供帮助信息

这个设计已经很好了！

#### 补充：支持配置文件方式

对于高级用户，提供配置文件方式：

```bash
# 复制模板
cp .env.example .env

# 编辑配置
vim .env

# 直接运行学习（跳过交互）
python3 learn_full_kb.py --auto
python3 build_full_kb_index.py
```

---

### 问题4：依赖管理

如何处理Python依赖？

#### 推荐方案

```bash
# requirements.txt
numpy>=1.24.0
scikit-learn>=1.3.0
rank-bm25>=0.2.2
jieba>=0.42.1
lark-oapi>=1.2.0
loguru>=0.7.0
pyyaml>=6.0
```

用户安装：
```bash
pip install -r requirements.txt
```

**OpenClaw集成时的考虑：**
- OpenClaw可能有自己的依赖管理
- 确保依赖版本兼容
- 考虑提供`setup.py`或`pyproject.toml`

---

### 问题5：OpenClaw集成

如何让Skill在OpenClaw中工作？

#### 当前实现

```markdown
# SKILL.md
---
name: feishu-kb
description: 飞书离线知识库检索...
---
```

```json
// _meta.json
{
  "name": "feishu-kb",
  "version": "1.0.0",
  "entry": "skill_main.py"
}
```

#### 挑战

1. **OpenClaw Skills通常期望即开即用**
   - 通用Skill需要初始化，不符合"即开即用"

2. **后台任务限制**
   - 大型数据下载（10-30分钟）不适合Skill激活时执行

3. **交互式输入**
   - OpenClaw后台可能不支持`input()`

#### 解决方案

在 `SKILL.md` 中明确标识需要初始化：

```markdown
---
name: feishu-kb
description: 飞书离线知识库检索...
requires_setup: true
---

## ⚠️ 首次使用前需要初始化

此Skill需要先配置和学习您的飞书知识库。

### 初始化步骤

1. 进入Skill目录:
   \`\`\`bash
   cd ~/.openclaw/workspace/skills/feishu-kb
   \`\`\`

2. 安装依赖:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. 运行初始化:
   \`\`\`bash
   python3 init_kb.py
   \`\`\`

4. 按照向导完成配置（约10-30分钟）

### 完成后即可使用

\`\`\`bash
python3 skill_main.py search "你的查询"
\`\`\`

或通过OpenClaw调用: `/feishu-kb search "查询"`
```

---

## 🎯 完整通用化方案

### GitHub仓库结构

```
feishu-offline-kb-skill/
├── README.md                  # 完整使用文档
├── SKILL.md                   # OpenClaw Skill定义
├── _meta.json                 # Skill元数据
├── requirements.txt           # Python依赖（明确版本）
├── .env.example               # 配置模板（不含真实凭证）
├── .gitignore                 # 排除data/, .env, logs/
├── LICENSE                    # 开源许可证
│
├── init_kb.py                 # ✨ 初始化向导
├── skill_main.py              # Skill入口
├── learn_full_kb.py           # 知识库学习
├── build_full_kb_index.py     # 索引构建
├── verify_system.py           # 系统验证
│
├── docs/                      # 设计文档
│   ├── INCREMENTAL_UPDATE_DESIGN.md
│   └── GENERALIZATION_DESIGN.md
│
├── src/                       # 核心代码
│   ├── retriever/
│   │   └── simple_search.py
│   └── utils/
│       ├── smart_chunker.py
│       └── config.py
│
├── data/                      # ❌ 不提交到Git
│   └── .gitkeep
│
└── logs/                      # ❌ 不提交到Git
    └── .gitkeep
```

### .gitignore

```gitignore
# 数据文件（用户自己生成）
data/
!data/.gitkeep

# 配置文件（包含敏感信息）
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# 日志
logs/
!logs/.gitkeep
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

### .env.example

```bash
# 飞书应用凭证
# 获取方法: https://open.feishu.cn/ → 创建企业自建应用
FEISHU_APP_ID=your_app_id_here
FEISHU_APP_SECRET=your_app_secret_here

# 知识库配置
# 支持三种方式:
#   1. Space ID (数字): 7480754861085147139
#   2. Wiki Token: N9kgwANVwi...
#   3. 或留空，使用URL方式（在init_kb.py中输入）
FEISHU_WIKI_SPACE_ID=
FEISHU_WIKI_TOKEN=
```

### README.md 结构

```markdown
# 飞书离线知识库检索 Skill

基于飞书知识库的完全离线检索系统，支持OpenClaw集成。

## ✨ 特性

- 🔍 智能混合检索（TF-IDF + BM25 + RRF融合）
- 💾 完全离线运行（构建后无需网络）
- ⚡ 极速响应（查询延迟 <100ms）
- 🎯 支持任意飞书知识库
- 📦 轻量级（索引仅占~20MB）

## 📋 前置要求

1. Python 3.8+
2. 飞书企业自建应用（获取App ID和Secret）
3. 对目标知识库的访问权限

## 🚀 快速开始

### 1. 克隆仓库

\`\`\`bash
git clone https://github.com/your-name/feishu-offline-kb-skill
cd feishu-offline-kb-skill
\`\`\`

### 2. 安装依赖

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 3. 初始化知识库

\`\`\`bash
python3 init_kb.py
\`\`\`

按照交互式向导完成：
- ✅ 输入飞书应用凭证
- ✅ 指定要学习的知识库
- ✅ 选择学习模式（测试/限制/完整）
- ✅ 自动下载和构建索引

⏱️ 首次初始化约需10-30分钟（取决于知识库大小）

### 4. 开始使用

\`\`\`bash
# 基本搜索
python3 skill_main.py search "你的查询"

# 查看状态
python3 skill_main.py status

# 更新知识库
python3 skill_main.py update
\`\`\`

## 🔧 获取飞书凭证

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 获取 **App ID** 和 **App Secret**
4. 开通权限：
   - 查看、评论和导出文档
   - 获取知识库信息
   - 获取知识空间信息

详细步骤：[飞书开发者文档](https://open.feishu.cn/document/home/introduction-to-custom-app-development/self-built-application-development-process)

## 🎮 使用方法

### 基本搜索

\`\`\`bash
python3 skill_main.py search "扫码王有哪些型号"
\`\`\`

### 指定检索模式

\`\`\`bash
# 向量检索（语义相似）
python3 skill_main.py search "收钱吧APP功能" --mode vector

# 关键词检索（精确匹配）
python3 skill_main.py search "商户进件流程" --mode keyword

# 混合检索（推荐，默认）
python3 skill_main.py search "支付业务" --mode hybrid
\`\`\`

### 高级选项

\`\`\`bash
# 返回更多结果
python3 skill_main.py search "扫码王" --top-k 10

# JSON格式输出
python3 skill_main.py search "扫码王" --format json
\`\`\`

## 🔄 更新知识库

当飞书知识库有更新时：

\`\`\`bash
python3 skill_main.py update
\`\`\`

支持断点续传，可随时 Ctrl+C 中断。

## 🔌 OpenClaw 集成

### 安装为OpenClaw Skill

\`\`\`bash
# 创建符号链接
ln -s $(pwd) ~/.openclaw/workspace/skills/feishu-kb

# 验证安装
openclaw skills | grep feishu-kb
\`\`\`

### ⚠️ 首次使用前需要初始化

\`\`\`bash
cd ~/.openclaw/workspace/skills/feishu-kb
python3 init_kb.py
\`\`\`

### 使用

\`\`\`bash
# 通过OpenClaw调用
/feishu-kb search "你的查询"
\`\`\`

## 📊 系统架构

\`\`\`
知识库规模（示例）:
  - 文档总数: 1,597 个
  - 文档块数: 7,476 个
  - 总字符数: 约310万
  - 向量维度: 768

检索引擎:
  - 向量检索: TF-IDF (sklearn)
  - 关键词检索: BM25Okapi
  - 混合检索: RRF融合
  - 存储: NumPy + SQLite + Pickle

性能指标:
  - 加载时间: ~2秒
  - 查询延迟: <100ms
  - 内存占用: ~200MB
  - 存储空间: ~20MB
\`\`\`

## 🛠️ 高级配置

### 配置文件方式

\`\`\`bash
# 复制配置模板
cp .env.example .env

# 编辑配置
vim .env

# 手动运行学习
python3 learn_full_kb.py --auto
python3 build_full_kb_index.py
\`\`\`

### 定时更新

\`\`\`bash
# 添加到crontab
crontab -e

# 每周日凌晨2点更新
0 2 * * 0 cd /path/to/feishu-kb && python3 skill_main.py update >> logs/update.log 2>&1
\`\`\`

## 🐛 故障排查

### 问题1: 搜索无结果

\`\`\`bash
# 检查索引状态
python3 skill_main.py status

# 验证系统
python3 verify_system.py
\`\`\`

### 问题2: 索引未构建

\`\`\`bash
# 重新构建索引
python3 build_full_kb_index.py
\`\`\`

### 问题3: 飞书API错误

- 检查 `.env` 中的凭证是否正确
- 确认应用已发布且权限已开通
- 验证对知识库的访问权限

## 📚 相关文档

- [增量更新方案](docs/INCREMENTAL_UPDATE_DESIGN.md)
- [通用化设计](docs/GENERALIZATION_DESIGN.md)
- [OpenClaw Skill文档](SKILL.md)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [飞书开放平台](https://open.feishu.cn/)
- [OpenClaw](https://github.com/anthropics/openclaw)

---

**快速链接**:
- [初始化指南](#-快速开始)
- [使用方法](#-使用方法)
- [故障排查](#-故障排查)
```

---

## 🎯 用户使用流程

### 新用户首次使用

```bash
# 1. 克隆仓库（<1分钟）
git clone https://github.com/user/feishu-kb-skill
cd feishu-kb-skill

# 2. 安装依赖（1-2分钟）
pip install -r requirements.txt

# 3. 初始化（10-30分钟）
python3 init_kb.py
# → 输入飞书凭证
# → 输入知识库URL
# → 选择学习模式
# → 等待完成

# 4. 使用（<100ms响应）
python3 skill_main.py search "查询"
```

### OpenClaw用户

```bash
# 1. 安装Skill
ln -s /path/to/feishu-kb ~/.openclaw/workspace/skills/feishu-kb

# 2. 初始化
cd ~/.openclaw/workspace/skills/feishu-kb
python3 init_kb.py

# 3. 使用
/feishu-kb search "查询"
```

---

## 📝 关键文件清单

### 必须创建/修改的文件

- [x] `init_kb.py` - 已创建，交互式初始化向导
- [x] `SKILL.md` - 已创建，需补充"requires_setup: true"说明
- [x] `_meta.json` - 已创建
- [ ] `README.md` - 需要完整重写（按上面模板）
- [ ] `.gitignore` - 需要创建
- [ ] `.env.example` - 需要创建
- [ ] `requirements.txt` - 需要创建（明确版本）
- [ ] `LICENSE` - 需要选择（建议MIT）

### 需要修改的文件

- [ ] `skill_main.py` - 添加初始化检测和提示
- [ ] `learn_full_kb.py` - 确保支持`--auto`模式
- [ ] `build_full_kb_index.py` - 确保无交互运行

### 文档文件

- [x] `docs/INCREMENTAL_UPDATE_DESIGN.md` - 已创建
- [x] `docs/GENERALIZATION_DESIGN.md` - 本文档

---

## 🎉 总结

### 核心策略

1. **不包含数据** - 保持GitHub仓库轻量
2. **首次使用时初始化** - 明确的初始化步骤
3. **交互式向导** - 友好的配置体验
4. **支持多种方式** - URL/Space ID/Token
5. **完善的文档** - README + 设计文档

### 实施优先级

**P0（必须）：**
- 创建 `.gitignore` 排除 `data/` 和 `.env`
- 创建 `.env.example` 配置模板
- 创建 `requirements.txt` 明确依赖
- 重写 `README.md` 完整使用说明
- 修改 `SKILL.md` 添加初始化说明

**P1（重要）：**
- 修改 `skill_main.py` 添加初始化检测
- 添加 `LICENSE` 文件
- 验证所有脚本支持非交互模式

**P2（可选）：**
- 添加 `setup.py` 或 `pyproject.toml`
- 创建示例截图和视频
- 多语言README（英文）

### 预期效果

发布后，用户体验：
```
1. git clone → 3秒
2. pip install → 1分钟
3. python3 init_kb.py → 10-30分钟（一次性）
4. 开始使用 → <100ms响应
```

**总时间投入：11-31分钟（一次性）**
**后续使用：即时响应，完全离线**

---

**文档版本**: v1.0
**创建日期**: 2026-03-08
**作者**: Claude Code
