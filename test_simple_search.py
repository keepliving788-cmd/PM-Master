#!/usr/bin/env python3
"""
测试SimpleSearchEngine
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.config import Config
from retriever.simple_search import SimpleSearchEngine

def main():
    print("=" * 70)
    print("测试SimpleSearchEngine")
    print("=" * 70)

    # 加载配置
    config = Config.load()

    # 初始化搜索引擎
    print("\n[1] 初始化搜索引擎...")
    search_engine = SimpleSearchEngine(config)
    print("✅ 初始化完成")

    # 测试查询
    test_queries = [
        ("扫码王", "hybrid"),
        ("收钱吧APP", "keyword"),
        ("产品白皮书", "vector"),
    ]

    for query, mode in test_queries:
        print(f"\n{'='*70}")
        print(f"查询: {query} (模式: {mode})")
        print('=' * 70)

        results = search_engine.search(query, top_k=3, mode=mode)

        if results:
            for i, result in enumerate(results, 1):
                print(f"\n{i}. 【分数: {result['score']:.3f}】")
                print(f"   标题: {result.get('doc_title', 'N/A')}")
                print(f"   内容: {result['content'][:200]}...")
        else:
            print("  未找到结果")

    print("\n" + "=" * 70)
    print("✅ 测试完成")
    print("=" * 70)

if __name__ == '__main__':
    main()
