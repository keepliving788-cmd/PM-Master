#!/usr/bin/env python3
"""
快速构建离线知识库 - 使用HuggingFace镜像或TF-IDF
"""
import sys
import os
from pathlib import Path

# 设置HuggingFace镜像
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

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
    print("🚀 快速构建离线知识库")
    print("=" * 70)

    # 加载配置
    config = Config.load()

    # 读取原始内容
    print("\n[1] 读取知识库内容...")
    content_file = Path('data/raw/wiki_content.txt')

    if not content_file.exists():
        print("❌ 未找到 data/raw/wiki_content.txt")
        return False

    with open(content_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"✅ 加载完成: {len(content)} 字符")

    # 智能分块
    print("\n[2] 智能分块...")
    chunker = SmartChunker(config)
    chunks = chunker.chunk_document(
        text=content,
        doc_id="sqb_product_kb",
        title="收钱吧产品知识库"
    )
    print(f"✅ 生成 {len(chunks)} 个文档块")

    # 尝试加载Embedding模型
    print("\n[3] 加载Embedding模型...")
    try:
        print("   尝试使用 m3e-base (通过镜像)...")
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer('moka-ai/m3e-base', device='cpu')
        print("✅ m3e-base 模型加载成功")

        # 生成向量
        print("\n[4] 生成向量嵌入...")
        texts = [chunk['content'] for chunk in chunks]
        embeddings = model.encode(
            texts,
            show_progress_bar=True,
            batch_size=32,
            normalize_embeddings=True
        )
        embeddings = np.array(embeddings)
        print(f"✅ 向量生成完成: {embeddings.shape}")

    except Exception as e:
        print(f"⚠️  m3e-base 下载失败: {e}")
        print("   使用 TF-IDF 向量作为备选方案...")

        # 使用TF-IDF
        from sklearn.feature_extraction.text import TfidfVectorizer

        texts = [chunk['content'] for chunk in chunks]
        vectorizer = TfidfVectorizer(max_features=768)
        embeddings = vectorizer.fit_transform(texts).toarray()

        # 保存vectorizer
        with open('data/tfidf_vectorizer.pkl', 'wb') as f:
            pickle.dump(vectorizer, f)

        print(f"✅ TF-IDF 向量生成完成: {embeddings.shape}")

    # 保存索引
    print("\n[5] 保存索引...")
    save_index(chunks, embeddings, config)

    print("\n" + "=" * 70)
    print("✅ 离线知识库构建完成！")
    print("=" * 70)
    print(f"\n数据统计:")
    print(f"  - 文档块数: {len(chunks)}")
    print(f"  - 向量维度: {embeddings.shape[1]}")
    print(f"  - 总字符数: {len(content)}")

    print(f"\n测试命令:")
    print(f"  python3 test_search.py")

    return True

def save_index(chunks, embeddings, config):
    """保存索引数据"""
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)

    # 保存向量
    np.savez_compressed(
        data_dir / 'vectors.npz',
        vectors=embeddings
    )
    print("   ✅ 向量已保存")

    # 构建BM25索引
    tokenized_corpus = [
        list(jieba.cut(chunk['content']))
        for chunk in chunks
    ]
    bm25 = BM25Okapi(tokenized_corpus)

    with open(data_dir / 'bm25_index.pkl', 'wb') as f:
        pickle.dump(bm25, f)
    print("   ✅ BM25索引已保存")

    # 保存到SQLite
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
    print("   ✅ 数据库已保存")

    # 保存元数据
    metadata = {
        'build_time': time.strftime("%Y-%m-%d %H:%M:%S"),
        'chunk_count': len(chunks),
        'vector_dimension': embeddings.shape[1],
        'model': 'moka-ai/m3e-base or TF-IDF'
    }

    with open(data_dir / 'metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print("   ✅ 元数据已保存")

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
