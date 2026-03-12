# 飞书应用配置指南

## 📋 配置流程概览

```
1. 创建飞书应用 (5分钟)
2. 配置权限 (2分钟)
3. 获取凭证 (1分钟)
4. 填入配置 (1分钟)
5. 测试连接 (1分钟)
```

总耗时：约 10 分钟

---

## 步骤 1: 创建飞书应用

### 1.1 访问飞书开放平台

打开浏览器，访问：
```
https://open.feishu.cn/
```

### 1.2 登录并进入开发者后台

1. 点击右上角【登录】
2. 使用你的飞书账号登录
3. 登录后，点击【开发者后台】或【进入控制台】

### 1.3 创建应用

1. 点击【创建企业自建应用】
2. 填写应用信息：
   - **应用名称**: `知识库检索助手`（或任何你喜欢的名称）
   - **应用描述**: `离线检索飞书产品知识库`
   - **应用图标**: 可选，上传或跳过
3. 点击【创建】

### 1.4 记录应用凭证

创建成功后，你会看到：

```
App ID: cli_xxxxxxxxxxxxxxxxx
App Secret: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**⚠️ 重要：请立即复制保存这些信息！**

---

## 步骤 2: 配置权限

### 2.1 进入权限管理

在应用详情页面：
1. 找到左侧菜单【权限管理】
2. 点击进入

### 2.2 添加知识库权限

在权限列表中，搜索并添加以下权限：

#### 必需权限：

1. **知识库相关**
   - `wiki:wiki:readonly` - 获取知识空间信息
   - 描述：允许应用读取知识库内容
   - 点击【申请权限】→【确定】

2. **文档相关**
   - `docx:document:readonly` - 查看文档
   - 描述：允许应用读取文档内容
   - 点击【申请权限】→【确定】

#### 可选权限（推荐）：

3. **用户信息**
   - `contact:user.base:readonly` - 获取用户基本信息
   - 用途：获取文档作者信息
   - 点击【申请权限】→【确定】

### 2.3 权限配置完成

配置完成后，你应该看到：

```
✅ wiki:wiki:readonly - 已开通
✅ docx:document:readonly - 已开通
✅ contact:user.base:readonly - 已开通（可选）
```

---

## 步骤 3: 发布应用

### 3.1 创建版本

1. 找到左侧菜单【版本管理与发布】
2. 点击【创建版本】
3. 填写版本信息：
   - **版本号**: `1.0.0`
   - **版本说明**: `初始版本`
4. 点击【保存】

### 3.2 申请发布

1. 点击【申请线上发布】
2. 选择【全部员工可见】（或根据需要选择范围）
3. 提交申请

### 3.3 审核发布

- 如果你是管理员：可以自己审批
- 否则：需要等待管理员审批

**审批通过后，应用状态变为【已发布】**

---

## 步骤 4: 配置本地环境

### 4.1 创建配置文件

```bash
cd "Feishu PKB"

# 复制配置模板
cp .env.example .env
```

### 4.2 编辑配置文件

使用任何文本编辑器打开 `.env`：

```bash
# macOS
nano .env

# 或
vim .env

# 或
code .env  # VSCode
```

### 4.3 填入配置

将步骤 1.4 记录的凭证填入：

```bash
# 飞书应用配置
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxxx          # 替换为你的 App ID
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxx    # 替换为你的 App Secret

# 知识库配置
FEISHU_WIKI_SPACE_ID=N9kgwANVwifcisk9UT6cDOFInRe

# 模型配置（保持默认即可）
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2

# 数据目录（保持默认即可）
DATA_DIR=./data
CHROMADB_DIR=./data/chromadb

# 日志配置（保持默认即可）
LOG_LEVEL=INFO
LOG_FILE=./logs/feishu-pkb.log
```

**保存文件**：
- nano: `Ctrl+O` → `Enter` → `Ctrl+X`
- vim: `ESC` → `:wq` → `Enter`

---

## 步骤 5: 测试连接

### 5.1 运行测试脚本

```bash
python test_api_access.py
```

### 5.2 预期输出

**成功的情况：**
```
============================================================
飞书 API 访问测试
============================================================

[1] 检查环境变量...
✅ App ID: cli_xxxxxx...
✅ App Secret: ********************
✅ Space ID: N9kgwANVwifcisk9UT6cDOFInRe

[2] 创建飞书客户端...
✅ 客户端创建成功

[3] 测试获取知识空间节点...
✅ 成功获取 10 个节点

节点列表：
   1. docx - Token: xxxxxxxxx
   2. wiki - Token: xxxxxxxxx
   3. docx - Token: xxxxxxxxx
   ...

============================================================

🎉 测试通过！可以开始构建索引了

下一步：
  python src/main.py index --full
```

### 5.3 如果测试失败

查看错误信息并参考下面的故障排查部分。

---

## 常见错误排查

### 错误 1: `99991663` - 权限不足

**错误信息：**
```
❌ API 调用失败
   错误码: 99991663
   错误信息: permission denied
```

**原因：**
- 应用未开启 `wiki:wiki:readonly` 权限
- 应用未发布或未添加到企业

**解决：**
1. 回到飞书开放平台
2. 检查【权限管理】→ 确认权限已开通
3. 检查【版本管理】→ 确认应用已发布
4. 等待 1-2 分钟后重试

---

### 错误 2: `99991401` - 认证失败

**错误信息：**
```
❌ API 调用失败
   错误码: 99991401
   错误信息: invalid app_id or app_secret
```

**原因：**
- App ID 或 App Secret 不正确
- 复制时多了空格或换行

**解决：**
1. 重新复制 App ID 和 App Secret
2. 确保没有多余的空格
3. 重新编辑 `.env` 文件

---

### 错误 3: `99991404` - 资源不存在

**错误信息：**
```
❌ API 调用失败
   错误码: 99991404
   错误信息: space not found
```

**原因：**
- Space ID 不正确
- 应用没有权限访问该知识空间

**解决：**
1. 确认 Space ID 是否正确
2. 访问知识库页面，检查 URL 中的 ID
3. 确保应用有权限访问该空间

**如何获取正确的 Space ID：**
```
知识库 URL:
https://sqb.feishu.cn/wiki/N9kgwANVwifcisk9UT6cDOFInRe?fromScene=spaceOverview
                            ^^^^^^^^^^^^^^^^^^^^^^^^
                            这就是 Space ID
```

---

### 错误 4: 无法连接飞书服务器

**错误信息：**
```
❌ 异常: Connection timeout
```

**原因：**
- 网络问题
- 防火墙阻止

**解决：**
1. 检查网络连接
2. 尝试访问 https://open.feishu.cn
3. 检查代理设置
4. 如果在公司网络，联系 IT 部门

---

## 验证清单

在运行测试前，请确认：

- [ ] 已创建飞书应用
- [ ] 已添加 `wiki:wiki:readonly` 权限
- [ ] 已添加 `docx:document:readonly` 权限
- [ ] 应用已发布（状态显示"已发布"）
- [ ] 已复制 App ID 到 `.env` 文件
- [ ] 已复制 App Secret 到 `.env` 文件
- [ ] Space ID 正确填写
- [ ] `.env` 文件保存成功

---

## 下一步

### 测试通过后

1. **构建索引**
   ```bash
   python src/main.py index --full
   ```

2. **等待索引完成**
   - 根据文档数量，可能需要 5-30 分钟
   - 会显示进度条

3. **开始检索**
   ```bash
   python src/main.py search "你的查询"
   ```

### 需要帮助？

- 查看完整文档：`README.md`
- 查看架构设计：`ARCHITECTURE.md`
- 遇到问题：提交 GitHub Issue

---

## 附录：飞书开放平台文档

- **开放平台首页**: https://open.feishu.cn/
- **Wiki API 文档**: https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/wiki-overview
- **权限说明**: https://open.feishu.cn/document/ukTMukTMukTM/uQjN3QjL0YzN04CN2cDN
- **API 错误码**: https://open.feishu.cn/document/ukTMukTMukTM/ugjM14COyUjL4ITN

---

**准备好了吗？** 现在开始配置你的飞书应用吧！
