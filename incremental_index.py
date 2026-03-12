#!/usr/bin/env python3
"""
增量更新知识库索引
将新文档增量添加到现有索引中
"""
import sys
import os
from pathlib import Path
import json
import time
import numpy as np
import pickle
import sqlite3
from rank_bm25 import BM25Okapi
import jieba

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.smart_chunker import SmartChunker
from utils.config import Config


def load_existing_index():
    """加载现有索引"""
    data_dir = Path('data')

    # 检查索引是否存在
    required_files = [
        data_dir / 'vectors.npz',
        data_dir / 'bm25_index.pkl',
        data_dir / 'kb_data.db',
        data_dir / 'metadata.json'
    ]

    if not all(f.exists() for f in required_files):
        return None

    print("📂 加载现有索引...")

    # 加载向量
    vectors_data = np.load(data_dir / 'vectors.npz')
    vectors = vectors_data['vectors']
    print(f"   ✅ 向量: {vectors.shape}")

    # 加载BM25索引
    with open(data_dir / 'bm25_index.pkl', 'rb') as f:
        bm25 = pickle.load(f)
    print(f"   ✅ BM25索引: {len(bm25.doc_freqs)} 文档")

    # 加载元数据
    with open(data_dir / 'metadata.json') as f:
        metadata = json.load(f)
    print(f"   ✅ 元数据: {metadata['chunk_count']} 块")

    # 连接数据库
    conn = sqlite3.connect(data_dir / 'kb_data.db')
    print(f"   ✅ 数据库连接成功")

    return {
        'vectors': vectors,
        'bm25': bm25,
        'metadata': metadata,
        'db_conn': conn
    }


def get_embedding_model():
    """获取Embedding模型"""
    try:
        print("📦 加载Embedding模型...")

        # 尝试加载 sentence-transformers
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('moka-ai/m3e-base', device='cpu')
        print("   ✅ m3e-base 模型")
        return model, 'transformer'

    except Exception as e:
        print(f"   ⚠️  m3e-base 不可用: {e}")

        # 尝试加载已保存的TF-IDF vectorizer
        tfidf_path = Path('data/tfidf_vectorizer.pkl')
        if tfidf_path.exists():
            with open(tfidf_path, 'rb') as f:
                vectorizer = pickle.load(f)
            print("   ✅ TF-IDF vectorizer")
            return vectorizer, 'tfidf'
        else:
            print("   ❌ 未找到任何可用的向量化模型")
            return None, None


def add_document_to_index(doc_path: str, existing_index: dict = None):
    """
    将新文档添加到索引中

    Args:
        doc_path: 文档路径
        existing_index: 现有索引（如果为None，则创建新索引）
    """
    print("=" * 70)
    print("🔨 增量更新索引")
    print("=" * 70)

    # 加载配置
    config = Config.load()

    # 读取新文档
    print(f"\n📄 读取文档: {doc_path}")
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"   ✅ {len(content)} 字符")

    # 提取标题
    lines = content.split('\n')
    title = lines[0].strip('# ').strip() if lines else "新文档"
    doc_id = Path(doc_path).stem

    # 智能分块
    print("\n✂️  文档分块...")
    chunker = SmartChunker(config)
    new_chunks = chunker.chunk_document(
        text=content,
        doc_id=doc_id,
        title=title
    )
    print(f"   ✅ 生成 {len(new_chunks)} 个块")

    # 获取Embedding模型
    model, model_type = get_embedding_model()
    if not model:
        print("❌ 无法加载向量化模型")
        return False

    # 生成新文档的向量
    print("\n🔢 生成向量...")
    texts = [chunk['content'] for chunk in new_chunks]

    if model_type == 'transformer':
        new_embeddings = model.encode(
            texts,
            show_progress_bar=True,
            batch_size=32,
            normalize_embeddings=True
        )
        new_embeddings = np.array(new_embeddings)
    else:  # tfidf
        new_embeddings = model.transform(texts).toarray()

    print(f"   ✅ 向量形状: {new_embeddings.shape}")

    # 如果存在旧索引，合并；否则创建新索引
    if existing_index:
        print("\n🔄 合并到现有索引...")
        updated_index = merge_index(existing_index, new_chunks, new_embeddings)
    else:
        print("\n🆕 创建新索引...")
        updated_index = create_new_index(new_chunks, new_embeddings)

    # 保存更新后的索引
    print("\n💾 保存索引...")
    save_updated_index(updated_index, config)

    print("\n" + "=" * 70)
    print("✅ 增量索引更新完成！")
    print("=" * 70)
    print(f"\n新增:")
    print(f"  - 文档: 1")
    print(f"  - 块数: {len(new_chunks)}")
    print(f"  - 总块数: {updated_index['metadata']['chunk_count']}")

    return True


def merge_index(existing_index, new_chunks, new_embeddings):
    """合并新索引到现有索引"""
    # 合并向量
    merged_vectors = np.vstack([
        existing_index['vectors'],
        new_embeddings
    ])
    print(f"   ✅ 向量: {existing_index['vectors'].shape} + {new_embeddings.shape} = {merged_vectors.shape}")

    # 更新BM25索引
    # 获取现有的tokenized corpus
    old_corpus = existing_index['bm25'].corpus_size
    new_tokenized = [list(jieba.cut(chunk['content'])) for chunk in new_chunks]

    # 重建BM25（需要包含新旧所有文档）
    # 从数据库读取所有旧文档内容
    cursor = existing_index['db_conn'].cursor()
    cursor.execute('SELECT content FROM chunks ORDER BY embedding_index')
    old_contents = [row[0] for row in cursor.fetchall()]
    old_tokenized = [list(jieba.cut(content)) for content in old_contents]

    merged_tokenized = old_tokenized + new_tokenized
    merged_bm25 = BM25Okapi(merged_tokenized)
    print(f"   ✅ BM25: {old_corpus} + {len(new_chunks)} = {merged_bm25.corpus_size} 文档")

    # 更新数据库
    cursor = existing_index['db_conn'].cursor()
    base_index = existing_index['metadata']['chunk_count']

    for i, chunk in enumerate(new_chunks):
        cursor.execute('''
            INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            chunk['chunk_id'],
            chunk['doc_id'],
            chunk['doc_title'],
            chunk['content'],
            json.dumps(chunk['headers'], ensure_ascii=False),
            chunk['chunk_index'],
            base_index + i
        ))

    existing_index['db_conn'].commit()
    print(f"   ✅ 数据库: 添加 {len(new_chunks)} 条记录")

    # 更新元数据
    merged_metadata = existing_index['metadata'].copy()
    merged_metadata['chunk_count'] = base_index + len(new_chunks)
    merged_metadata['last_update'] = time.strftime("%Y-%m-%d %H:%M:%S")
    merged_metadata['incremental_updates'] = merged_metadata.get('incremental_updates', 0) + 1

    return {
        'vectors': merged_vectors,
        'bm25': merged_bm25,
        'metadata': merged_metadata,
        'db_conn': existing_index['db_conn']
    }


def create_new_index(chunks, embeddings):
    """创建新索引（首次使用）"""
    # 构建BM25
    tokenized_corpus = [list(jieba.cut(chunk['content'])) for chunk in chunks]
    bm25 = BM25Okapi(tokenized_corpus)

    # 创建数据库
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)

    db_path = data_dir / 'kb_data.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

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

    for i, chunk in enumerate(chunks):
        cursor.execute('''
            INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?)
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

    metadata = {
        'build_time': time.strftime("%Y-%m-%d %H:%M:%S"),
        'chunk_count': len(chunks),
        'vector_dimension': embeddings.shape[1],
        'model': 'moka-ai/m3e-base or TF-IDF',
        'incremental_updates': 0
    }

    return {
        'vectors': embeddings,
        'bm25': bm25,
        'metadata': metadata,
        'db_conn': conn
    }


def save_updated_index(index, config):
    """保存更新后的索引"""
    data_dir = Path('data')

    # 保存向量
    np.savez_compressed(
        data_dir / 'vectors.npz',
        vectors=index['vectors']
    )
    print("   ✅ 向量")

    # 保存BM25
    with open(data_dir / 'bm25_index.pkl', 'wb') as f:
        pickle.dump(index['bm25'], f)
    print("   ✅ BM25")

    # 数据库已在merge过程中更新，关闭连接
    index['db_conn'].close()
    print("   ✅ 数据库")

    # 保存元数据
    with open(data_dir / 'metadata.json', 'w', encoding='utf-8') as f:
        json.dump(index['metadata'], f, ensure_ascii=False, indent=2)
    print("   ✅ 元数据")


def main():
    if len(sys.argv) < 2:
        print("用法: python3 incremental_index.py <文档路径>")
        print("\n示例:")
        print("  python3 incremental_index.py data/raw/learned/learned_doxcnxxxxx.txt")
        sys.exit(1)

    doc_path = sys.argv[1]

    if not Path(doc_path).exists():
        print(f"❌ 文件不存在: {doc_path}")
        sys.exit(1)

    # 加载现有索引
    existing_index = load_existing_index()

    if existing_index:
        print("   ℹ️  将增量添加到现有索引\n")
    else:
        print("   ℹ️  将创建新索引\n")

    # 添加文档到索引
    success = add_document_to_index(doc_path, existing_index)

    if success:
        print("\n下一步: 重新加载搜索引擎或重启服务")

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
