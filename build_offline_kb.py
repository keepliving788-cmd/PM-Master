#!/usr/bin/env python3
"""
构建离线知识库
从原始文档构建高精度检索索引
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.smart_chunker import SmartChunker
from utils.embedder import HighPrecisionEmbedder
from utils.config import Config
import json
import time

def main():
    print("=" * 70)
    print("🚀 构建离线知识库")
    print("=" * 70)

    # 加载配置
    config = Config.load()

    # 读取原始内容
    print("\n[1] 读取知识库内容...")
    content_file = Path('data/raw/wiki_content.txt')

    if not content_file.exists():
        print("❌ 未找到 data/raw/wiki_content.txt")
        print("   请先运行: python3 fetch_wiki_content.py")
        return False

    with open(content_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"✅ 加载完成")
    print(f"   文件大小: {len(content)} 字符")

    # 初始化分块器
    print("\n[2] 智能分块...")
    chunker = SmartChunker(config)

    chunks = chunker.chunk_document(
        text=content,
        doc_id="sqb_product_kb",
        title="收钱吧产品知识库"
    )

    print(f"✅ 分块完成")
    print(f"   生成 {len(chunks)} 个文档块")

    # 显示示例
    if chunks:
        print(f"\n   示例块:")
        print(f"   - ID: {chunks[0]['chunk_id']}")
        print(f"   - Headers: {chunks[0]['headers']}")
        print(f"   - 内容: {chunks[0]['content'][:100]}...")

    # 初始化Embedder
    print("\n[3] 加载Embedding模型...")
    embedder = HighPrecisionEmbedder(config)

    # 生成向量
    print("\n[4] 生成向量嵌入...")
    texts = [chunk['content'] for chunk in chunks]
    embeddings = embedder.encode_documents(texts, show_progress=True)

    print(f"✅ 向量生成完成")
    print(f"   Shape: {embeddings.shape}")

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

    print(f"\n下一步:")
    print(f"  python3 src/main.py search \"扫码王有哪些型号\"")

    return True

def save_index(chunks, embeddings, config):
    """保存索引数据"""
    import numpy as np
    import pickle
    import sqlite3
    from rank_bm25 import BM25Okapi
    import jieba

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
        'model': config.indexing['embedding']['model_name']
    }

    with open(data_dir / 'metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print("   ✅ 元数据已保存")

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
