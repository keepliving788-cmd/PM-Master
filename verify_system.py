#!/usr/bin/env python3
"""
系统验证脚本 - 检查所有组件是否正常
"""
from pathlib import Path
import sys

def check_files():
    """检查必要文件"""
    print("=" * 70)
    print("检查文件...")
    print("=" * 70)

    required_files = [
        'data/raw/wiki_content.txt',
        'data/vectors.npz',
        'data/bm25_index.pkl',
        'data/tfidf_vectorizer.pkl',
        'data/kb_data.db',
        'data/metadata.json',
    ]

    all_ok = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            print(f"  ✅ {file_path} ({size} bytes)")
        else:
            print(f"  ❌ {file_path} 不存在")
            all_ok = False

    return all_ok

def check_metadata():
    """检查元数据"""
    print("\n" + "=" * 70)
    print("检查元数据...")
    print("=" * 70)

    import json
    try:
        with open('data/metadata.json', 'r') as f:
            metadata = json.load(f)

        print(f"  构建时间: {metadata['build_time']}")
        print(f"  文档块数: {metadata['chunk_count']}")
        print(f"  向量维度: {metadata['vector_dimension']}")
        print(f"  模型: {metadata['model']}")
        return True
    except Exception as e:
        print(f"  ❌ 读取元数据失败: {e}")
        return False

def check_search_engine():
    """检查检索引擎"""
    print("\n" + "=" * 70)
    print("检查检索引擎...")
    print("=" * 70)

    sys.path.insert(0, 'src')

    try:
        from utils.config import Config
        from retriever.simple_search import SimpleSearchEngine

        config = Config.load()
        search_engine = SimpleSearchEngine(config)

        # 测试搜索
        results = search_engine.search("扫码王", top_k=3, mode='hybrid')

        print(f"  ✅ 检索引擎加载成功")
        print(f"  ✅ 测试查询返回 {len(results)} 个结果")

        if results:
            print(f"\n  示例结果:")
            result = results[0]
            print(f"    分数: {result['score']:.3f}")
            print(f"    内容: {result['content'][:100]}...")

        return True

    except Exception as e:
        print(f"  ❌ 检索引擎测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database():
    """检查数据库"""
    print("\n" + "=" * 70)
    print("检查数据库...")
    print("=" * 70)

    import sqlite3

    try:
        conn = sqlite3.connect('data/kb_data.db')
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM chunks')
        count = cursor.fetchone()[0]

        cursor.execute('SELECT chunk_id, doc_title FROM chunks LIMIT 1')
        row = cursor.fetchone()

        conn.close()

        print(f"  ✅ 数据库连接成功")
        print(f"  ✅ 文档块数: {count}")
        print(f"  ✅ 示例块: {row[0]} - {row[1]}")

        return True

    except Exception as e:
        print(f"  ❌ 数据库检查失败: {e}")
        return False

def main():
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "系统验证检查" + " " * 36 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    checks = [
        ("文件检查", check_files),
        ("元数据检查", check_metadata),
        ("数据库检查", check_database),
        ("检索引擎检查", check_search_engine),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n  ❌ {name}异常: {e}")
            results.append((name, False))

    # 总结
    print("\n" + "=" * 70)
    print("检查总结")
    print("=" * 70)

    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
        if not result:
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 系统验证完全通过！")
        print("=" * 70)
        print("\n可以启动服务了：")
        print("  ./start_bot.sh")
        print("\n或直接运行：")
        print("  python3 bot_server.py")
    else:
        print("⚠️  部分检查未通过")
        print("=" * 70)
        print("\n请检查失败的项目并修复")

    print()
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
