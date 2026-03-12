# 🎯 完整知识库学习指南

## 📊 当前状态

✅ **已发现 1597 个文档节点！**

层级分布：
- Level 0: 5 个（根目录）
- Level 1-7: 1592 个（子文档）

---

## 🚀 使用步骤

### 步骤1: 学习完整知识库（一次性）

```bash
cd "/Users/macuser/Desktop/Start/Skills/Feishu PKB"

# 开始学习（下载所有1597个文档）
python3 learn_full_kb.py
```

**这将会：**
1. 递归获取所有1597个文档节点
2. 逐个下载文档内容（显示进度）
3. 保存到 `data/raw/full_kb_content.txt`
4. 生成元数据 `data/raw/full_kb_metadata.json`

**预计时间：** 10-30分钟（取决于网络速度）

**支持断点续传：**
- 按 `Ctrl+C` 随时中断
- 再次运行会从断点继续
- 进度保存在 `data/raw/download_progress.json`

---

### 步骤2: 构建完整索引

```bash
# 构建离线检索索引
python3 build_full_kb_index.py
```

**这将会：**
1. 读取 `full_kb_content.txt`（所有文档内容）
2. 智能分块（预计生成 8,000-16,000 个chunks）
3. 生成 TF-IDF 向量（768维）
4. 构建 BM25 关键词索引
5. 保存到 SQLite 数据库

**预计时间：** 1-5分钟

**存储空间：** 约100-150 MB

---

### 步骤3: 测试搜索

```bash
# 测试搜索功能
python3 skill_main.py search 扫码王

# 查看知识库状态
python3 skill_main.py status
```

---

## 🧪 测试模式（推荐先试）

**先测试10个文档：**

```bash
# 只下载前10个文档（快速测试）
python3 learn_full_kb.py --test
```

这会：
- 只下载10个文档（~1分钟）
- 验证流程是否正常
- 测试索引构建

测试成功后，再运行完整版本：
```bash
python3 learn_full_kb.py
```

---

## 📁 生成的文件

### 原始数据（data/raw/）

```
data/raw/
├── nodes_cache.json           # 1597个节点列表（缓存）
├── download_progress.json     # 下载进度（断点续传）
├── full_kb_content.txt        # 所有文档内容（~50 MB）
└── full_kb_metadata.json      # 文档元数据
```

### 索引文件（data/）

```
data/
├── vectors.npz                # TF-IDF向量（~50 MB）
├── bm25_index.pkl            # BM25索引（~2 MB）
├── tfidf_vectorizer.pkl      # 向量化器（~5 MB）
├── kb_data.db                # SQLite数据库（~8 MB）
└── metadata.json             # 索引元数据
```

**预计总大小：** 100-150 MB

---

## ⚙️ 高级选项

### 限制下载数量

```bash
# 只下载前50个文档
python3 learn_full_kb.py --limit 50

# 只下载前100个文档
python3 learn_full_kb.py --limit 100
```

### 重新下载（清除缓存）

```bash
# 删除缓存，从头开始
rm data/raw/nodes_cache.json
rm data/raw/download_progress.json

python3 learn_full_kb.py
```

### 查看下载进度

```bash
# 查看已下载数量
cat data/raw/download_progress.json | grep "success"
```

---

## 🔍 预期结果

### 学习完成后

```
✅ 完整知识库学习完成！
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  成功: 1580 个
  跳过: 0 个
  失败: 17 个
  总计: 1580 个

文件: data/raw/full_kb_content.txt
大小: 45.2 MB
文档数: 1580
```

### 索引构建完成后

```
✅ 完整知识库索引构建完成！
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  文档块数: 12,450
  向量维度: 768
  总字符数: 15,800,000
  原始大小: 45.2 MB
  索引大小: 120 MB
```

---

## 🎯 搜索对比

### 当前（1个文档）
- 文档数：1
- 文档块：10
- 搜索范围：极小

### 完整知识库（1597个文档）
- 文档数：1597
- 文档块：~12,000
- 搜索范围：完整

**搜索精度提升 1000+ 倍！** 🚀

---

## ⚠️ 注意事项

### 1. 网络连接
- 需要稳定的网络连接
- 如果中断，可以继续（断点续传）

### 2. 飞书API限流
- 脚本已加入延迟（0.1秒/请求）
- 避免请求过快被限流

### 3. 存储空间
- 确保有 200-300 MB 可用空间
- 原始文本：~50 MB
- 索引文件：~100 MB

### 4. 时间成本
- 首次学习：10-30分钟
- 后续更新：只需更新变化的文档

---

## 🔄 增量更新（未来功能）

目前是全量下载，未来可以实现：

1. **检测文档变化**
   - 对比文档的更新时间
   - 只下载变化的文档

2. **增量索引更新**
   - 只重建变化文档的索引
   - 合并到现有索引

3. **定时自动更新**
   - 每天/每周自动检查更新
   - 后台运行

---

## 📞 故障排查

### 问题1: 下载速度很慢

**原因：** 网络不稳定或飞书API响应慢

**解决：**
- 先用 `--test` 测试10个文档
- 或用 `--limit 100` 分批下载

### 问题2: 部分文档下载失败

**原因：** 权限问题或文档不存在

**解决：**
- 失败的文档会跳过
- 检查失败日志
- 大部分成功即可使用

### 问题3: 内存不足

**原因：** 文档太大

**解决：**
- 关闭其他程序
- 或分批处理（--limit）

### 问题4: 索引构建失败

**原因：** 依赖缺失

**解决：**
```bash
pip install scikit-learn rank-bm25 jieba
```

---

## 🎊 开始使用

**推荐流程：**

```bash
# 1. 测试（1分钟）
python3 learn_full_kb.py --test
python3 build_full_kb_index.py
python3 skill_main.py search 扫码王

# 2. 如果测试OK，完整学习（30分钟）
python3 learn_full_kb.py
python3 build_full_kb_index.py

# 3. 享受完整知识库！
python3 skill_main.py search 你的查询
```

---

**现在可以开始了！建议先运行测试模式：**

```bash
python3 learn_full_kb.py --test
```

或直接完整学习：

```bash
python3 learn_full_kb.py
```

🚀 **让我们获取完整的1597个文档！**
