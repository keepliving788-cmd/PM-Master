# 📖 如何获取飞书知识库Space ID

## ❌ 当前问题

你配置的是 **Wiki Token**，不是 **Space ID**：
- Wiki Token: `N9kgwANVwifcisk9UT6cDOFInRe` ❌
- Space ID应该是: **纯数字格式**，例如 `7480754861085147139` ✅

---

## 🔍 方法1：从URL获取（最简单）

### 步骤：

1. 打开飞书，进入你的知识库
2. 查看浏览器地址栏的URL

### URL格式示例：

```
https://your-company.feishu.cn/wiki/N9kgwANVwifcisk9UT6cDOFInRe
                                     ↑
                              这是 Wiki Token

或者：

https://your-company.feishu.cn/wiki/space/7480754861085147139
                                          ↑
                                   这是 Space ID（纯数字）
```

### 判断方法：

- **如果URL包含纯数字** → 那就是Space ID ✅
- **如果URL只有混合字符** → 需要用下面的方法2或3

---

## 🛠️ 方法2：使用测试脚本获取

我为你创建了一个脚本来自动查找Space ID：

```bash
cd "/Users/macuser/Desktop/Start/Skills/Feishu PKB"
python3 find_space_id.py
```

这个脚本会：
1. 列出你有权限访问的所有知识空间
2. 显示每个空间的名称和对应的Space ID
3. 你可以从中选择正确的那个

---

## 🔧 方法3：通过飞书开放平台API调试工具

### 步骤：

1. 访问：https://open.feishu.cn/api-explorer
2. 搜索API：`wiki/v2/spaces`
3. 填入你的 App ID 和 App Secret
4. 点击"发送请求"
5. 在返回结果中查找：

```json
{
  "data": {
    "items": [
      {
        "name": "收钱吧产品知识库",
        "space_id": "7480754861085147139",  ← 这个就是Space ID！
        "space_type": "team"
      }
    ]
  }
}
```

---

## ✏️ 配置正确的Space ID

获得正确的Space ID后，编辑 `.env` 文件：

```bash
nano .env
```

修改为：

```env
FEISHU_APP_ID=cli_a91379879838dcee
FEISHU_APP_SECRET=yi5ChxR1vRQ5jR8LGRxQxd4fi5g7tPRl
FEISHU_WIKI_SPACE_ID=7480754861085147139  ← 改成实际的Space ID（纯数字）
```

保存后测试：

```bash
python3 test_api_access.py
```

---

## 💡 Wiki Token vs Space ID

| 项目 | Wiki Token | Space ID |
|------|-----------|----------|
| 格式 | 混合字符 | 纯数字 |
| 示例 | N9kgwANVwifcisk9UT6cDOFInRe | 7480754861085147139 |
| 用途 | 标识特定Wiki页面 | 标识整个知识空间 |
| 本项目需要 | ❌ | ✅ |

---

## 🎯 快速解决方案

如果你不确定Space ID，运行我创建的脚本：

```bash
python3 find_space_id.py
```

它会自动列出所有可用的知识空间，让你选择正确的那个。

---

## ❓ 仍然有问题？

### 可能原因1：应用权限不足

确保你的飞书应用有以下权限：
- ✅ `wiki:wiki:readonly` - 读取知识库
- ✅ `docx:document:readonly` - 读取文档

### 可能原因2：应用未发布

1. 进入飞书开放平台
2. 找到你的应用
3. 点击"发布应用"
4. 等待审核通过

### 可能原因3：不在应用管理员组

联系管理员，确保你的账号有权限访问该知识空间。

---

## 📞 需要帮助？

1. 查看详细日志：
   ```bash
   tail -50 logs/feishu-pkb.log
   ```

2. 查看飞书API文档：
   https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/wiki-overview

3. 运行完整诊断：
   ```bash
   ./quick_start.sh
   ```
