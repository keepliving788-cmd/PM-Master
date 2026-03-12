"""
搜索引擎 - 统一的检索接口
"""
from typing import List, Dict, Optional
from loguru import logger

from .vector_search import VectorSearch
from .keyword_search import KeywordSearch
from .hybrid_search import HybridSearch
from ..storage.doc_store import DocumentStore


class SearchEngine:
    """搜索引擎"""

    def __init__(self, config):
        """
        初始化搜索引擎

        Args:
            config: 配置对象
        """
        self.config = config

        # 初始化各种检索器
        self.vector_search = VectorSearch(config)
        self.keyword_search = KeywordSearch(config)
        self.hybrid_search = HybridSearch(config)

        # 初始化文档存储
        self.doc_store = DocumentStore(config)

        logger.info("搜索引擎初始化完成")

    def search(
        self,
        query: str,
        top_k: int = 5,
        mode: str = 'hybrid',
        threshold: float = 0.7
    ) -> List[Dict]:
        """
        搜索文档

        Args:
            query: 查询字符串
            top_k: 返回结果数量
            mode: 检索模式 (vector | keyword | hybrid)
            threshold: 相似度阈值

        Returns:
            搜索结果列表
        """
        logger.info(f"开始检索: query='{query}', mode={mode}, top_k={top_k}")

        try:
            if mode == 'vector':
                results = self.vector_search.search(query, top_k)
            elif mode == 'keyword':
                results = self.keyword_search.search(query, top_k)
            elif mode == 'hybrid':
                results = self.hybrid_search.search(query, top_k)
            else:
                logger.error(f"未知的检索模式: {mode}")
                return []

            # 过滤低相似度结果
            results = [r for r in results if r['score'] >= threshold]

            # 增强结果信息
            enriched_results = []
            for result in results:
                doc = self.doc_store.get_document(result['doc_id'])
                if doc:
                    enriched_results.append({
                        **result,
                        'title': doc['title'],
                        'url': self._build_doc_url(result['doc_id']),
                        'created_at': doc['created_at'],
                        'updated_at': doc['updated_at']
                    })

            logger.info(f"检索完成，返回 {len(enriched_results)} 个结果")
            return enriched_results

        except Exception as e:
            logger.error(f"检索失败: {e}")
            return []

    def get_document(self, doc_id: str) -> Optional[Dict]:
        """
        获取文档详情

        Args:
            doc_id: 文档 ID

        Returns:
            文档详情
        """
        doc = self.doc_store.get_document(doc_id)

        if doc:
            doc['url'] = self._build_doc_url(doc_id)

        return doc

    def get_stats(self) -> Dict:
        """
        获取统计信息

        Returns:
            统计信息
        """
        docs = self.doc_store.list_documents()

        total_chars = sum(doc.get('metadata', {}).get('char_count', 0) for doc in docs)
        total_chunks = sum(doc.get('metadata', {}).get('chunk_count', 0) for doc in docs)

        return {
            'total_docs': len(docs),
            'total_chunks': total_chunks,
            'total_chars': total_chars,
            'avg_chars_per_doc': total_chars / len(docs) if docs else 0,
            'last_updated': max((doc['updated_at'] for doc in docs), default='N/A'),
            'index_version': '1.0',
            'storage_size': self._get_storage_size()
        }

    def _build_doc_url(self, doc_id: str) -> str:
        """构建文档 URL"""
        space_id = self.config.feishu['wiki_space_id']
        return f"https://sqb.feishu.cn/wiki/{space_id}/{doc_id}"

    def _get_storage_size(self) -> str:
        """获取存储大小"""
        # TODO: 实现存储大小计算
        return "N/A"
