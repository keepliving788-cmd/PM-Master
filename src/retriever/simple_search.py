"""
简化版检索引擎 - 直接使用NumPy和SQLite
支持实时图片内容理解
"""
import numpy as np
import sqlite3
import pickle
import jieba
from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger


class SimpleSearchEngine:
    """简化版检索引擎"""

    def __init__(self, config):
        """初始化检索引擎"""
        self.config = config
        data_dir = Path('data')

        # 加载向量
        logger.info("加载向量索引...")
        vectors_data = np.load(data_dir / 'vectors.npz')
        self.vectors = vectors_data['vectors']
        logger.info(f"  向量维度: {self.vectors.shape}")

        # 加载BM25
        logger.info("加载BM25索引...")
        with open(data_dir / 'bm25_index.pkl', 'rb') as f:
            self.bm25 = pickle.load(f)

        # 加载数据库
        logger.info("加载文档数据库...")
        self.db_path = data_dir / 'kb_data.db'

        # 加载TF-IDF Vectorizer
        logger.info("加载向量化器...")
        tfidf_path = data_dir / 'tfidf_vectorizer.pkl'
        if tfidf_path.exists():
            with open(tfidf_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            self.use_tfidf = True
            logger.info("  使用 TF-IDF")
        else:
            # 尝试加载 m3e-base
            try:
                from utils.embedder import HighPrecisionEmbedder
                self.embedder = HighPrecisionEmbedder(config)
                self.use_tfidf = False
                logger.info("  使用 m3e-base")
            except Exception as e:
                raise Exception(f"未找到可用的向量化器: {e}")

        logger.info("✅ 检索引擎加载完成")

    def search(self, query: str, top_k: int = 5, mode: str = 'hybrid') -> List[Dict]:
        """
        搜索

        Args:
            query: 查询字符串
            top_k: 返回结果数量
            mode: 检索模式 (vector | keyword | hybrid)

        Returns:
            搜索结果列表
        """
        logger.info(f"检索: '{query}' (mode={mode})")

        if mode == 'vector':
            return self._vector_search(query, top_k)
        elif mode == 'keyword':
            return self._keyword_search(query, top_k)
        elif mode == 'hybrid':
            return self._hybrid_search(query, top_k)
        else:
            logger.error(f"未知模式: {mode}")
            return []

    def _vector_search(self, query: str, top_k: int) -> List[Dict]:
        """向量检索"""
        # 查询向量化
        if self.use_tfidf:
            query_vec = self.vectorizer.transform([query]).toarray()[0]
        else:
            query_vec = self.embedder.encode_query(query)

        # 计算相似度
        similarities = np.dot(self.vectors, query_vec)

        # 获取top-k
        top_indices = np.argsort(similarities)[::-1][:top_k]

        # 获取文档内容
        results = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for rank, idx in enumerate(top_indices, 1):
            cursor.execute(
                'SELECT chunk_id, content, doc_title FROM chunks WHERE embedding_index = ?',
                (int(idx),)
            )
            row = cursor.fetchone()
            if row:
                results.append({
                    'chunk_id': row[0],
                    'content': row[1],
                    'doc_title': row[2],
                    'score': float(similarities[idx]),
                    'rank': rank
                })

        conn.close()
        return results

    def _keyword_search(self, query: str, top_k: int) -> List[Dict]:
        """关键词检索 (BM25)"""
        # 分词
        query_tokens = list(jieba.cut(query))

        # BM25打分
        scores = self.bm25.get_scores(query_tokens)

        # 获取top-k
        top_indices = np.argsort(scores)[::-1][:top_k]

        # 获取文档内容
        results = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for rank, idx in enumerate(top_indices, 1):
            cursor.execute(
                'SELECT chunk_id, content, doc_title FROM chunks WHERE embedding_index = ?',
                (int(idx),)
            )
            row = cursor.fetchone()
            if row:
                results.append({
                    'chunk_id': row[0],
                    'content': row[1],
                    'doc_title': row[2],
                    'score': float(scores[idx]),
                    'rank': rank
                })

        conn.close()
        return results

    def _hybrid_search(self, query: str, top_k: int) -> List[Dict]:
        """混合检索 (RRF融合)"""
        # 分别检索
        vector_results = self._vector_search(query, top_k * 3)
        keyword_results = self._keyword_search(query, top_k * 3)

        # RRF融合
        rrf_scores = {}
        k = 60  # RRF常数

        for result in vector_results:
            chunk_id = result['chunk_id']
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1 / (k + result['rank'])

        for result in keyword_results:
            chunk_id = result['chunk_id']
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1 / (k + result['rank'])

        # 按分数排序
        sorted_chunks = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        # 获取完整结果
        results = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for rank, (chunk_id, score) in enumerate(sorted_chunks, 1):
            cursor.execute(
                'SELECT content, doc_title FROM chunks WHERE chunk_id = ?',
                (chunk_id,)
            )
            row = cursor.fetchone()
            if row:
                results.append({
                    'chunk_id': chunk_id,
                    'content': row[0],
                    'doc_title': row[1],
                    'score': score,
                    'rank': rank
                })

        conn.close()
        return results

    def enrich_with_images(self, results: List[Dict], enable_images: bool = True) -> List[Dict]:
        """
        为检索结果增强图片内容理解

        Args:
            results: 检索结果列表
            enable_images: 是否启用图片理解

        Returns:
            增强后的结果列表
        """
        if not enable_images:
            return results

        try:
            from utils.image_handler import get_image_handler

            image_handler = get_image_handler()
            enriched_results = []

            for result in results:
                content = result['content']

                # 检测是否包含图片引用
                image_refs = image_handler.extract_image_references(content)

                if not image_refs:
                    # 无图片，保持原样
                    enriched_results.append(result)
                    continue

                logger.info(f"检测到 {len(image_refs)} 个图片引用")

                # 增强结果
                enriched_result = result.copy()
                enriched_result['content'] += f"\n\n⚠️ 此段落包含 {len(image_refs)} 张图片"
                enriched_result['has_images'] = True
                enriched_result['image_count'] = len(image_refs)
                enriched_result['image_refs'] = image_refs

                enriched_results.append(enriched_result)

            return enriched_results

        except Exception as e:
            logger.error(f"图片增强失败: {e}")
            return results  # 失败时返回原结果
