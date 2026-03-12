# 配置检查清单

在运行 `python test_api_access.py` 之前，请使用这个清单确认所有配置正确。

## ✅ 配置检查清单

### 1. 飞书应用创建

- [ ] 已访问 https://open.feishu.cn/
- [ ] 已登录飞书账号
- [ ] 已创建企业自建应用
- [ ] 应用名称：________________

### 2. 应用凭证

- [ ] 已获取 App ID（格式：cli_xxxxx）
- [ ] 已获取 App Secret（长字符串）
- [ ] 已保存凭证到安全位置

### 3. 权限配置

- [ ] 已添加权限：`wiki:wiki:readonly`
- [ ] 已添加权限：`docx:document:readonly`
- [ ] 权限状态显示：已开通

### 4. 应用发布

- [ ] 已创建版本（版本号：1.0.0）
- [ ] 已申请发布
- [ ] 发布已审批通过
- [ ] 应用状态：已发布

### 5. 本地配置

- [ ] 已进入项目目录
- [ ] 已复制 `.env.example` 到 `.env`
- [ ] 已编辑 `.env` 文件
- [ ] 已填入 `FEISHU_APP_ID`
- [ ] 已填入 `FEISHU_APP_SECRET`
- [ ] 已确认 `FEISHU_WIKI_SPACE_ID=N9kgwANVwifcisk9UT6cDOFInRe`
- [ ] 已保存 `.env` 文件

### 6. 环境依赖

- [ ] 已安装 Python 3.9+
- [ ] 已运行 `pip install -r requirements.txt`
- [ ] 已运行 `make setup` 或手动创建 data 目录

### 7. 网络连接

- [ ] 可以访问 https://open.feishu.cn
- [ ] 可以访问 https://sqb.feishu.cn
- [ ] 网络无代理问题

---

## 🔍 快速验证

### 验证 .env 文件

```bash
# 查看配置（隐藏敏感信息）
cat .env | grep -E "FEISHU_APP_ID|FEISHU_APP_SECRET|FEISHU_WIKI_SPACE_ID"
```

**预期输出：**
```
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxx
FEISHU_WIKI_SPACE_ID=N9kgwANVwifcisk9UT6cDOFInRe
```

### 验证依赖安装

```bash
# 检查关键依赖
python -c "import lark_oapi; print('✅ lark-oapi installed')"
python -c "import chromadb; print('✅ chromadb installed')"
python -c "from dotenv import load_dotenv; print('✅ python-dotenv installed')"
```

**预期输出：**
```
✅ lark-oapi installed
✅ chromadb installed
✅ python-dotenv installed
```

### 验证目录结构

```bash
ls -la data/
```

**预期输出：**
```
drwxr-xr-x  chromadb
drwxr-xr-x  processed
drwxr-xr-x  raw
```

---

## 🚀 准备测试

### 所有检查通过？

运行测试脚本：
```bash
python test_api_access.py
```

### 测试失败？

参考 [SETUP_GUIDE.md](SETUP_GUIDE.md) 的故障排查部分。

---

## 📞 获取帮助

### 常见问题

**Q: App ID 格式不对？**
- App ID 应该以 `cli_` 开头
- 长度约 20 个字符
- 示例：`cli_a1b2c3d4e5f6g7h8`

**Q: App Secret 包含特殊字符？**
- App Secret 可能包含特殊字符
- 在 .env 中不需要加引号
- 直接粘贴即可

**Q: Space ID 从哪里获取？**
- 打开知识库页面
- 查看浏览器地址栏
- 提取 `/wiki/` 后面的 ID

**Q: 权限开通了但还是失败？**
- 等待 1-2 分钟让权限生效
- 确认应用已发布
- 检查应用版本状态

---

**下一步**：参考 [SETUP_GUIDE.md](SETUP_GUIDE.md) 完成详细配置
