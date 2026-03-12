#!/usr/bin/env python3
"""
构建完整知识库索引 - 使用 full_kb_content.txt
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.smart_chunker import SmartChunker
from utils.config import Config
import json
import time
import numpy as np
import pickle
import sqlite3
from rank_bm25 import BM25Okapi
import jieba


def main():
    print("=" * 70)
    print("🚀 构建完整知识库索引")
    print("=" * 70)

    # 检查文件
    content_file = Path('data/raw/full_kb_content.txt')
    if not content_file.exists():
        print("❌ 未找到 data/raw/full_kb_content.txt")
        print("   请先运行: python3 learn_full_kb.py")
        return False

    # 加载配置
    config = Config.load()

    # 读取内容
    print("\n[1] 读取完整知识库内容...")
    with open(content_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"✅ 加载完成")
    print(f"   文件大小: {len(content):,} 字符 ({len(content)/1024/1024:.2f} MB)")

    # 智能分块
    print("\n[2] 智能分块...")
    chunker = SmartChunker(config)

    chunks = chunker.chunk_document(
        text=content,
        doc_id="full_kb",
        title="收钱吧完整产品知识库"
    )

    print(f"✅ 分块完成")
    print(f"   生成 {len(chunks):,} 个文档块")

    if chunks:
        print(f"\n   示例块:")
        print(f"   - ID: {chunks[0]['chunk_id']}")
        print(f"   - 内容: {chunks[0]['content'][:100]}...")

    # 生成向量
    print("\n[3] 生成向量嵌入...")
    print("   使用 TF-IDF (快速方案)...")

    from sklearn.feature_extraction.text import TfidfVectorizer

    texts = [chunk['content'] for chunk in chunks]
    vectorizer = TfidfVectorizer(max_features=768)
    embeddings = vectorizer.fit_transform(texts).toarray()

    print(f"✅ 向量生成完成")
    print(f"   Shape: {embeddings.shape}")
    print(f"   文档块: {embeddings.shape[0]:,}")
    print(f"   向量维度: {embeddings.shape[1]}")

    # 保存索引
    print("\n[4] 保存索引...")
    save_index(chunks, embeddings, vectorizer, config)

    print("\n" + "=" * 70)
    print("✅ 完整知识库索引构建完成！")
    print("=" * 70)

    print(f"\n数据统计:")
    print(f"  - 文档块数: {len(chunks):,}")
    print(f"  - 向量维度: {embeddings.shape[1]}")
    print(f"  - 总字符数: {len(content):,}")
    print(f"  - 原始大小: {len(content)/1024/1024:.2f} MB")

    print(f"\n下一步:")
    print(f"  python3 test_simple_search.py")
    print(f"  python3 skill_main.py search 扫码王")

    return True


def save_index(chunks, embeddings, vectorizer, config):
    """保存索引数据"""
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)

    # 保存向量
    print("   正在保存向量...", end=' ', flush=True)
    np.savez_compressed(
        data_dir / 'vectors.npz',
        vectors=embeddings
    )
    file_size = (data_dir / 'vectors.npz').stat().st_size
    print(f"✅ ({file_size/1024/1024:.1f} MB)")

    # 构建BM25索引
    print("   正在构建BM25索引...", end=' ', flush=True)
    tokenized_corpus = [
        list(jieba.cut(chunk['content']))
        for chunk in chunks
    ]
    bm25 = BM25Okapi(tokenized_corpus)

    with open(data_dir / 'bm25_index.pkl', 'wb') as f:
        pickle.dump(bm25, f)
    file_size = (data_dir / 'bm25_index.pkl').stat().st_size
    print(f"✅ ({file_size/1024/1024:.1f} MB)")

    # 保存TF-IDF向量化器
    print("   正在保存TF-IDF向量化器...", end=' ', flush=True)
    with open(data_dir / 'tfidf_vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    file_size = (data_dir / 'tfidf_vectorizer.pkl').stat().st_size
    print(f"✅ ({file_size/1024/1024:.1f} MB)")

    # 保存到SQLite
    print("   正在保存数据库...", end=' ', flush=True)
    db_path = data_dir / 'kb_data.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 创建表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id TEXT PRIMARY KEY,
            doc_id TEXT,
            doc_title TEXT,
            content TEXT,
            headers TEXT,
            chunk_index INTEGER,
            embedding_index INTEGER
        )
    ''')

    # 清空旧数据
    cursor.execute('DELETE FROM chunks')

    # 插入数据
    for i, chunk in enumerate(chunks):
        cursor.execute('''
            INSERT OR REPLACE INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            chunk['chunk_id'],
            chunk['doc_id'],
            chunk['doc_title'],
            chunk['content'],
            json.dumps(chunk['headers'], ensure_ascii=False),
            chunk['chunk_index'],
            i
        ))

    conn.commit()
    conn.close()
    file_size = db_path.stat().st_size
    print(f"✅ ({file_size/1024/1024:.1f} MB)")

    # 保存元数据
    metadata = {
        'build_time': time.strftime("%Y-%m-%d %H:%M:%S"),
        'chunk_count': len(chunks),
        'vector_dimension': embeddings.shape[1],
        'model': 'TF-IDF (sklearn)',
        'source': 'full_kb_content.txt'
    }

    with open(data_dir / 'metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print("   ✅ 元数据已保存")

    # 计算总存储
    total_size = sum([
        (data_dir / f).stat().st_size
        for f in ['vectors.npz', 'bm25_index.pkl', 'tfidf_vectorizer.pkl', 'kb_data.db']
        if (data_dir / f).exists()
    ])
    print(f"\n   📊 索引总大小: {total_size/1024/1024:.1f} MB")


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
