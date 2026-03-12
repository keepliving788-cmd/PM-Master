"""
向量检索
"""
from typing import List, Dict
from loguru import logger
from ..storage.vector_store import VectorStore


class VectorSearch:
    """向量检索器"""

    def __init__(self, config):
        """
        初始化向量检索器

        Args:
            config: 配置对象
        """
        self.config = config
        self.vector_store = VectorStore(config)

        self.top_k = config.retrieval['vector_search']['top_k']
        self.similarity_threshold = config.retrieval['vector_search']['similarity_threshold']

    def search(self, query: str, top_k: int = None) -> List[Dict]:
        """
        向量检索

        Args:
            query: 查询字符串
            top_k: 返回结果数量

        Returns:
            检索结果
        """
        if top_k is None:
            top_k = self.top_k

        logger.debug(f"向量检索: query='{query}', top_k={top_k}")

        try:
            # 查询向量数据库
            results = self.vector_store.query(query, n_results=top_k)

            # 格式化结果
            formatted_results = []
            for i, (doc_id, content, score) in enumerate(zip(
                results['ids'][0],
                results['documents'][0],
                results['distances'][0]
            )):
                # ChromaDB 返回的是距离，转换为相似度
                similarity = 1 - score

                formatted_results.append({
                    'doc_id': doc_id.split('_')[0],  # 提取文档 ID
                    'chunk_id': doc_id,
                    'content': content,
                    'score': similarity,
                    'rank': i + 1
                })

            return formatted_results

        except Exception as e:
            logger.error(f"向量检索失败: {e}")
            return []
