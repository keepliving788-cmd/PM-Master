"""
关键词检索 - 使用 BM25 算法
"""
from typing import List, Dict
from rank_bm25 import BM25Okapi
from loguru import logger

from ..storage.doc_store import DocumentStore


class KeywordSearch:
    """关键词检索器"""

    def __init__(self, config):
        """
        初始化关键词检索器

        Args:
            config: 配置对象
        """
        self.config = config
        self.doc_store = DocumentStore(config)

        self.top_k = config.retrieval['keyword_search']['top_k']
        self.k1 = config.retrieval['keyword_search']['k1']
        self.b = config.retrieval['keyword_search']['b']

        # 构建 BM25 索引
        self._build_bm25_index()

    def _build_bm25_index(self):
        """构建 BM25 索引"""
        logger.info("构建 BM25 索引...")

        # 获取所有文档
        docs = self.doc_store.list_documents()

        # 准备文档列表
        self.documents = []
        self.doc_ids = []

        for doc in docs:
            for chunk in doc.get('chunks', []):
                self.documents.append(chunk['content'])
                self.doc_ids.append({
                    'doc_id': doc['doc_id'],
                    'chunk_id': chunk['chunk_id'],
                    'title': doc['title']
                })

        # 分词（简单的空格分词，可以改用 jieba）
        tokenized_corpus = [doc.split() for doc in self.documents]

        # 构建 BM25 模型
        self.bm25 = BM25Okapi(tokenized_corpus, k1=self.k1, b=self.b)

        logger.info(f"BM25 索引构建完成，共 {len(self.documents)} 个文档块")

    def search(self, query: str, top_k: int = None) -> List[Dict]:
        """
        关键词检索

        Args:
            query: 查询字符串
            top_k: 返回结果数量

        Returns:
            检索结果
        """
        if top_k is None:
            top_k = self.top_k

        logger.debug(f"关键词检索: query='{query}', top_k={top_k}")

        try:
            # 分词查询
            tokenized_query = query.split()

            # BM25 检索
            scores = self.bm25.get_scores(tokenized_query)

            # 获取 top-k 结果
            top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

            # 格式化结果
            results = []
            for rank, idx in enumerate(top_indices, 1):
                doc_info = self.doc_ids[idx]
                results.append({
                    'doc_id': doc_info['doc_id'],
                    'chunk_id': doc_info['chunk_id'],
                    'title': doc_info['title'],
                    'content': self.documents[idx],
                    'score': float(scores[idx]),
                    'rank': rank
                })

            return results

        except Exception as e:
            logger.error(f"关键词检索失败: {e}")
            return []

    def reload_index(self):
        """重新加载索引"""
        self._build_bm25_index()
