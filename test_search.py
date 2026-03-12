#!/usr/bin/env python3
"""
测试离线知识库搜索
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.config import Config

def test_tfidf_search():
    """测试TF-IDF版本的搜索"""
    import numpy as np
    import sqlite3
    import pickle
    import jieba
    from sklearn.feature_extraction.text import TfidfVectorizer

    print("=" * 70)
    print("测试离线知识库搜索 (TF-IDF版本)")
    print("=" * 70)

    # 加载数据
    print("\n[1] 加载索引...")
    vectors_data = np.load('data/vectors.npz')
    vectors = vectors_data['vectors']
    print(f"   向量: {vectors.shape}")

    with open('data/bm25_index.pkl', 'rb') as f:
        bm25 = pickle.load(f)
    print(f"   BM25: 加载成功")

    with open('data/tfidf_vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    print(f"   TF-IDF Vectorizer: 加载成功")

    db_path = 'data/kb_data.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print(f"   数据库: 已连接")

    # 测试查询
    test_queries = [
        "扫码王",
        "收钱吧APP",
        "产品白皮书",
        "商户中心",
        "支付业务"
    ]

    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"查询: {query}")
        print('=' * 70)

        # 1. 向量检索 (TF-IDF)
        print("\n[向量检索 - TF-IDF]")
        query_vec = vectorizer.transform([query]).toarray()[0]
        similarities = np.dot(vectors, query_vec)
        top_indices = np.argsort(similarities)[::-1][:3]

        for i, idx in enumerate(top_indices, 1):
            cursor.execute(
                'SELECT content FROM chunks WHERE embedding_index = ?',
                (int(idx),)
            )
            row = cursor.fetchone()
            if row:
                print(f"\n  {i}. 【相似度: {similarities[idx]:.3f}】")
                print(f"     {row[0][:150]}...")

        # 2. 关键词检索 (BM25)
        print("\n[关键词检索 - BM25]")
        query_tokens = list(jieba.cut(query))
        scores = bm25.get_scores(query_tokens)
        top_indices = np.argsort(scores)[::-1][:3]

        for i, idx in enumerate(top_indices, 1):
            cursor.execute(
                'SELECT content FROM chunks WHERE embedding_index = ?',
                (int(idx),)
            )
            row = cursor.fetchone()
            if row:
                print(f"\n  {i}. 【BM25分数: {scores[idx]:.3f}】")
                print(f"     {row[0][:150]}...")

        # 3. 混合检索 (RRF)
        print("\n[混合检索 - RRF]")
        rrf_scores = {}
        k = 60

        # 向量结果
        vector_indices = np.argsort(similarities)[::-1][:10]
        for rank, idx in enumerate(vector_indices, 1):
            cursor.execute('SELECT chunk_id FROM chunks WHERE embedding_index = ?', (int(idx),))
            row = cursor.fetchone()
            if row:
                chunk_id = row[0]
                rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1 / (k + rank)

        # BM25结果
        bm25_indices = np.argsort(scores)[::-1][:10]
        for rank, idx in enumerate(bm25_indices, 1):
            cursor.execute('SELECT chunk_id FROM chunks WHERE embedding_index = ?', (int(idx),))
            row = cursor.fetchone()
            if row:
                chunk_id = row[0]
                rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1 / (k + rank)

        # 排序
        sorted_chunks = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:3]

        for i, (chunk_id, score) in enumerate(sorted_chunks, 1):
            cursor.execute('SELECT content FROM chunks WHERE chunk_id = ?', (chunk_id,))
            row = cursor.fetchone()
            if row:
                print(f"\n  {i}. 【RRF分数: {score:.3f}】")
                print(f"     {row[0][:150]}...")

    conn.close()

    print("\n" + "=" * 70)
    print("✅ 测试完成")
    print("=" * 70)

if __name__ == '__main__':
    test_tfidf_search()
