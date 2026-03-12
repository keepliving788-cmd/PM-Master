# 🚀 高精度检索系统部署指南

## 📦 准备工作

### 系统要求

- Python 3.9+
- 4GB+ 可用内存
- 2GB+ 磁盘空间（用于模型）
- 稳定的网络连接（首次下载模型）

---

## 🛠️ 部署步骤

### 第1步：安装依赖

```bash
cd "/Users/macuser/Desktop/Start/Skills/Feishu PKB"

# 安装所有依赖（包括新增的）
pip3 install -r requirements.txt

# 如果遇到网络问题，使用镜像源
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**预计耗时：** 3-5分钟

**常见问题：**

- **问题：** `torch` 安装失败
  ```bash
  # 解决方案：先单独安装torch
  pip3 install torch --index-url https://download.pytorch.org/whl/cpu
  ```

- **问题：** `lark-oapi` 版本冲突
  ```bash
  # 解决方案：强制重装
  pip3 install --force-reinstall lark-oapi>=1.2.0
  ```

### 第2步：验证安装

```bash
# 运行测试脚本
python3 test_upgraded_system.py
```

**预期输出：**
```
🚀 高精度检索系统 - 全面测试
================================================================================

📋 测试清单:
  1. ✅ 高精度Embedding模型
  2. ✅ 查询优化器
  3. ✅ 智能文档分块
  4. ⏸️  集成测试（需要索引）
  5. ✅ 性能基准

...

🎉 所有测试完成！
```

**注意：** 首次运行会自动下载模型（~400MB），需要等待5-10分钟。

### 第3步：配置飞书应用

如果还没有配置飞书应用，请参考 [SETUP_GUIDE.md](SETUP_GUIDE.md)

```bash
# 检查配置
cat .env

# 应该包含：
# FEISHU_APP_ID=cli_xxxxx
# FEISHU_APP_SECRET=xxxxxxxx
# FEISHU_WIKI_SPACE_ID=xxxxxxxx
```

### 第4步：重建索引

**重要：** 由于模型维度从384变为768，必须重建索引！

```bash
# 清理旧索引
rm -rf data/chromadb
rm -rf data/processed/*

# 全量构建新索引
python3 src/main.py index --full
```

**预计耗时：** 5-15分钟（取决于文档数量）

**过程监控：**
```bash
# 在另一个终端查看日志
tail -f logs/feishu-pkb.log
```

**预期输出：**
```
🚀 开始构建索引...
📥 加载Embedding模型: moka-ai/m3e-base
✓ 模型加载成功
  - 维度: 768
  - 设备: cpu

📚 获取文档列表...
✓ 找到 15 个文档

📥 下载文档内容...
✓ 处理完成 15/15 文档

✂️  智能分块...
✓ 生成 342 个文档块

🧠 生成向量嵌入...
100%|████████████████████| 342/342 [02:15<00:00,  2.53it/s]
✓ 生成 342 个向量 (维度: 768)

🔍 构建检索索引...
✓ 索引构建完成

✅ 索引构建完成！
  - 总文档数: 15
  - 新增文档: 15
  - 总耗时: 285.34秒
```

### 第5步：测试检索

```bash
# 测试基础检索
python3 src/main.py search "扫码王有哪些型号" --mode=hybrid

# 测试重排序模式（高精度）
python3 src/main.py search "如何开通富友通道" --mode=hybrid --top-k=10
```

**预期输出：**
```
找到 5 个相关结果：

================================================================================
[1] 产品介绍 - 扫码王系列
相关度: 0.856 | 文档ID: doc_xxxxx

扫码王系列产品包括SQ300、SQ500、SQ700等多个型号...

链接: https://feishu.cn/docx/xxxxx
...
```

---

## ✅ 验证清单

部署完成后，请确认以下项目：

- [ ] ✅ 依赖安装成功（`test_upgraded_system.py` 通过）
- [ ] ✅ 模型下载完成（`~/.cache/huggingface/hub/` 有模型文件）
- [ ] ✅ 飞书配置正确（`test_api_access.py` 通过）
- [ ] ✅ 索引构建成功（`data/chromadb/` 有数据文件）
- [ ] ✅ 检索功能正常（搜索返回相关结果）

---

## 🔧 配置优化

### 高精度模式（推荐）

`config/config.yaml`:

```yaml
indexing:
  embedding:
    model_name: moka-ai/m3e-base
    dimension: 768
    batch_size: 32

retrieval:
  weights:
    vector: 0.6
    keyword: 0.4
  rerank:
    enabled: true
    model: BAAI/bge-reranker-base
    initial_top_k: 30
    top_k: 10
```

### 快速模式（如果设备资源有限）

```yaml
indexing:
  embedding:
    model_name: paraphrase-multilingual-MiniLM-L12-v2
    dimension: 384
    batch_size: 64

retrieval:
  weights:
    vector: 0.5
    keyword: 0.5
  rerank:
    enabled: false
```

---

## 📊 性能监控

### 查看系统状态

```bash
# 查看索引统计
python3 src/main.py stats

# 查看日志
tail -100 logs/feishu-pkb.log

# 检查存储空间
du -sh data/
```

### 性能指标

**正常指标范围：**

| 指标 | 高精度模式 | 快速模式 |
|------|-----------|----------|
| 索引构建时间 | 5-15分钟 | 2-5分钟 |
| 单次检索延迟 | 200-500ms | 50-150ms |
| 内存占用 | 2-4GB | 1-2GB |
| 磁盘占用 | 1-2GB | 500MB-1GB |

---

## 🐛 常见问题

### Q1: 模型下载失败

**症状：** `HTTPError` 或 `Connection timeout`

**解决方案：**

```bash
# 方法1：使用镜像源
export HF_ENDPOINT=https://hf-mirror.com
pip3 install -r requirements.txt

# 方法2：手动下载（如果方法1失败）
mkdir -p ~/.cache/huggingface/hub
cd ~/.cache/huggingface/hub
git lfs install
git clone https://hf-mirror.com/moka-ai/m3e-base
```

### Q2: 内存不足

**症状：** `MemoryError` 或系统卡死

**解决方案：**

```yaml
# 减小batch_size
indexing:
  embedding:
    batch_size: 16  # 默认32

retrieval:
  rerank:
    batch_size: 8   # 默认16
```

### Q3: 重排序模型加载失败

**症状：** `Model BAAI/bge-reranker-base not found`

**解决方案：**

```yaml
# 暂时禁用重排序
retrieval:
  rerank:
    enabled: false
```

或使用备选模型：

```yaml
retrieval:
  rerank:
    model: cross-encoder/ms-marco-MiniLM-L-6-v2
```

### Q4: 索引构建卡住不动

**症状：** 进度条长时间停留在某个百分比

**诊断步骤：**

```bash
# 1. 查看日志
tail -f logs/feishu-pkb.log

# 2. 检查网络（可能是飞书API调用卡住）
python3 test_api_access.py

# 3. 检查系统资源
top  # 查看CPU和内存

# 4. 如果确认卡住，重启构建
pkill -f "main.py index"
python3 src/main.py index --full --force
```

### Q5: 检索结果不准确

**可能原因和解决方案：**

1. **索引未更新**
   ```bash
   python3 src/main.py sync
   ```

2. **模型不匹配**
   - 检查 `config.yaml` 中的模型名称
   - 确认索引是用当前模型构建的

3. **权重不合适**
   ```yaml
   retrieval:
     weights:
       vector: 0.7  # 提高语义权重
       keyword: 0.3
   ```

---

## 🔄 升级指南

从旧版本升级：

```bash
# 1. 备份数据
cp -r data data_backup_$(date +%Y%m%d)

# 2. 拉取更新
git pull origin main

# 3. 更新依赖
pip3 install -r requirements.txt --upgrade

# 4. 重建索引
rm -rf data/chromadb
python3 src/main.py index --full

# 5. 测试
python3 test_upgraded_system.py
```

---

## 🎯 下一步

部署完成后：

1. 📖 阅读 [UPGRADE_GUIDE.md](UPGRADE_GUIDE.md) 了解新功能
2. 🔍 运行实际查询测试效果
3. 📈 根据 [ARCHITECTURE.md](ARCHITECTURE.md) 了解系统架构
4. 🛠️ 根据使用场景调优配置

---

## 📞 获取帮助

遇到问题？

1. 查看 [README.md](README.md) 文档
2. 检查 [CHECK_CONFIG.md](CHECK_CONFIG.md) 配置清单
3. 查看日志 `logs/feishu-pkb.log`
4. 提交 Issue 或联系维护者

---

**版本**: 2.0.0-high-precision
**更新时间**: 2026-03-07
**状态**: ✅ 生产就绪
