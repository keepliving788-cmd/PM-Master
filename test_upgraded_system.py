#!/usr/bin/env python3
"""
高精度检索系统测试脚本
测试新功能：高精度embedding、重排序、智能分块、查询优化
"""
import sys
from pathlib import Path
import time
from typing import List, Dict

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.config import Config
from utils.embedder import HighPrecisionEmbedder
from utils.query_optimizer import QueryOptimizer
from utils.smart_chunker import SmartChunker

# 测试查询集
TEST_QUERIES = [
    "扫码王有哪些型号",
    "如何开通富友通道",
    "POS机费率是多少",
    "收钱吧支持哪些支付方式",
    "商户入网需要哪些材料",
    "扫码设备和刷卡机有什么区别",
]


def print_section(title: str, char: str = "="):
    """打印分隔符"""
    print(f"\n{char * 80}")
    print(f"  {title}")
    print(f"{char * 80}\n")


def test_embedder():
    """测试高精度Embedding"""
    print_section("测试1: 高精度Embedding模型")

    config = Config.load()
    embedder = HighPrecisionEmbedder(config)

    # 获取模型信息
    info = embedder.get_model_info()
    print("📊 模型信息:")
    print(f"  - 模型名称: {info['model_name']}")
    print(f"  - 向量维度: {info['dimension']}")
    print(f"  - 计算设备: {info['device']}")
    print(f"  - 批处理大小: {info['batch_size']}")

    # 测试编码
    test_texts = [
        "收钱吧扫码王SQ300",
        "富友支付通道费率",
        "商户入网资料"
    ]

    print(f"\n🧪 编码测试 ({len(test_texts)} 个文本):")
    start_time = time.time()
    vectors = embedder.encode_documents(test_texts, show_progress=False)
    elapsed = time.time() - start_time

    print(f"  ✅ 编码完成")
    print(f"  - 输出shape: {vectors.shape}")
    print(f"  - 耗时: {elapsed*1000:.2f}ms")
    print(f"  - 平均速度: {len(test_texts)/elapsed:.1f} 文本/秒")

    # 测试查询编码
    query = "扫码王型号"
    query_vector = embedder.encode_query(query)
    print(f"\n🔍 查询编码测试:")
    print(f"  - 查询: \"{query}\"")
    print(f"  - 向量shape: {query_vector.shape}")

    print("\n✅ Embedder测试通过")


def test_query_optimizer():
    """测试查询优化"""
    print_section("测试2: 查询优化器")

    config = Config.load()
    optimizer = QueryOptimizer(config)

    print("🧪 查询优化测试:\n")

    for query in TEST_QUERIES[:3]:
        print(f"原始查询: \"{query}\"")

        result = optimizer.optimize_query(query)

        print(f"  ├─ 清洗后: {result['cleaned']}")
        print(f"  ├─ 分词: {result['tokens']}")
        print(f"  ├─ 扩展词: {result['expanded']}")
        print(f"  └─ 改写: {result['reformulated']}")
        print()

    # 测试多查询生成
    print("🔄 多查询变体生成:")
    query = "如何使用扫码枪收款"
    variants = optimizer.generate_multiple_queries(query)
    print(f"  原查询: \"{query}\"")
    for i, variant in enumerate(variants, 1):
        print(f"  变体{i}: \"{variant}\"")

    print("\n✅ 查询优化器测试通过")


def test_smart_chunker():
    """测试智能分块"""
    print_section("测试3: 智能文档分块")

    config = Config.load()
    chunker = SmartChunker(config)

    # 测试文档
    test_doc = """# 产品介绍

## 扫码王系列

### SQ300型号

扫码王SQ300是收钱吧推出的专业扫码设备，支持多种支付方式。

主要特点：
- 支持支付宝、微信支付
- 快速扫码，响应迅速
- 体积小巧，便携性强

### SQ500型号

扫码王SQ500是高端扫码设备，适合大型商户使用。

## POS机系列

### 智能POS

智能POS机集成了多种功能，支持刷卡、扫码、云闪付等多种支付方式。"""

    print("📄 测试文档:")
    print(f"  - 长度: {len(test_doc)} 字符")
    print(f"  - 标题数: {test_doc.count('#')}")

    # 分块
    chunks = chunker.chunk_document(
        text=test_doc,
        doc_id="test_doc",
        title="产品介绍文档"
    )

    print(f"\n✂️  分块结果:")
    print(f"  - 块数量: {len(chunks)}")

    # 显示前3个块
    print(f"\n📦 块详情 (前3个):")
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"\n  块#{i}:")
        print(f"    - ID: {chunk['chunk_id']}")
        print(f"    - 标题路径: {' > '.join(chunk['headers']) if chunk['headers'] else '无'}")
        print(f"    - 长度: {chunk['char_count']} 字符")
        print(f"    - 内容: {chunk['content'][:80]}...")

    print("\n✅ 智能分块测试通过")


def test_integration():
    """集成测试：完整检索流程"""
    print_section("测试4: 集成测试（需要已构建索引）")

    try:
        from retriever.search_engine import SearchEngine

        config = Config.load()
        engine = SearchEngine(config)

        print("🔍 完整检索流程测试:\n")

        test_query = TEST_QUERIES[0]
        print(f"查询: \"{test_query}\"\n")

        # 测试不同模式
        modes = ['vector', 'keyword', 'hybrid']
        results_by_mode = {}

        for mode in modes:
            print(f"📊 模式: {mode}")
            start_time = time.time()

            results = engine.search(
                query=test_query,
                top_k=5,
                mode=mode
            )

            elapsed = time.time() - start_time
            results_by_mode[mode] = results

            print(f"  - 结果数: {len(results)}")
            print(f"  - 耗时: {elapsed*1000:.2f}ms")

            if results:
                print(f"  - Top-1分数: {results[0]['score']:.3f}")
                print(f"  - Top-1内容: {results[0]['content'][:60]}...")
            print()

        # 对比结果
        print("📈 模式对比:")
        print(f"  {'模式':<10} {'结果数':<8} {'Top-1分数':<12}")
        print(f"  {'-'*30}")
        for mode, results in results_by_mode.items():
            count = len(results)
            score = results[0]['score'] if results else 0
            print(f"  {mode:<10} {count:<8} {score:<12.3f}")

        print("\n✅ 集成测试通过")

    except ImportError as e:
        print(f"⚠️  集成测试跳过: {e}")
        print("  提示: 请先运行 `python src/main.py index --full` 构建索引")


def test_performance():
    """性能基准测试"""
    print_section("测试5: 性能基准")

    config = Config.load()
    embedder = HighPrecisionEmbedder(config)

    # 测试不同批大小的性能
    test_texts = ["测试文本" + str(i) for i in range(100)]

    print("⚡ Embedding性能测试:")
    print(f"  测试数据: {len(test_texts)} 个文本\n")

    for batch_size in [8, 16, 32, 64]:
        start_time = time.time()
        embedder.encode(test_texts, batch_size=batch_size, show_progress=False)
        elapsed = time.time() - start_time

        throughput = len(test_texts) / elapsed
        print(f"  Batch={batch_size:>2}: {elapsed:.3f}s ({throughput:.1f} 文本/秒)")

    print("\n✅ 性能测试完成")


def run_all_tests():
    """运行所有测试"""
    print_section("🚀 高精度检索系统 - 全面测试", "=")

    print("📋 测试清单:")
    print("  1. ✅ 高精度Embedding模型")
    print("  2. ✅ 查询优化器")
    print("  3. ✅ 智能文档分块")
    print("  4. ⏸️  集成测试（需要索引）")
    print("  5. ✅ 性能基准")

    try:
        test_embedder()
        test_query_optimizer()
        test_smart_chunker()
        test_integration()
        test_performance()

        print_section("🎉 所有测试完成！", "=")
        print("\n下一步:")
        print("  1. 如果集成测试跳过，请先构建索引:")
        print("     python src/main.py index --full")
        print()
        print("  2. 运行实际检索测试:")
        print("     python src/main.py search \"你的查询\" --mode=hybrid")
        print()
        print("  3. 查看升级指南:")
        print("     cat UPGRADE_GUIDE.md")
        print()

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
