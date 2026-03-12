"""
混合检索 - 结合向量检索和关键词检索
高精度版本: 支持重排序、智能去重、diversity-aware ranking
"""
from typing import List, Dict
from loguru import logger
import numpy as np

from .vector_search import VectorSearch
from .keyword_search import KeywordSearch
from .reranker import Reranker


class HybridSearch:
    """高精度混合检索器"""

    def __init__(self, config):
        """
        初始化混合检索器

        Args:
            config: 配置对象
        """
        self.config = config

        # 初始化子检索器
        self.vector_search = VectorSearch(config)
        self.keyword_search = KeywordSearch(config)

        # 初始化重排序器
        self.reranker = Reranker(config)

        # 检索权重
        self.vector_weight = config.retrieval['weights']['vector']
        self.keyword_weight = config.retrieval['weights']['keyword']

        # 融合方法
        self.fusion_method = config.retrieval['fusion']['method']
        self.rrf_k = config.retrieval['fusion']['rrf_k']

        # 重排序配置
        self.rerank_enabled = self.reranker.is_enabled()
        if self.rerank_enabled:
            self.rerank_initial_k = config.retrieval['rerank'].get('initial_top_k', 30)
            self.rerank_top_k = config.retrieval['rerank'].get('top_k', 10)
            logger.info(f"重排序已启用: {self.rerank_initial_k} → {self.rerank_top_k}")

        logger.success("混合检索引擎初始化完成")
        logger.info(f"  - 向量权重: {self.vector_weight}")
        logger.info(f"  - 关键词权重: {self.keyword_weight}")
        logger.info(f"  - 融合方法: {self.fusion_method}")
        logger.info(f"  - 重排序: {'启用' if self.rerank_enabled else '禁用'}")

    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        高精度混合检索（支持重排序）

        Args:
            query: 查询字符串
            top_k: 最终返回结果数量

        Returns:
            融合并重排序后的检索结果
        """
        logger.debug(f"混合检索: query='{query}', top_k={top_k}")

        try:
            # 如果启用重排序，先获取更多候选结果
            if self.rerank_enabled:
                initial_k = max(self.rerank_initial_k, top_k * 3)
                logger.debug(f"重排序模式: 初排序获取 {initial_k} 条候选")
            else:
                initial_k = top_k * 2

            # 分别执行向量检索和关键词检索
            vector_results = self.vector_search.search(query, top_k=initial_k)
            keyword_results = self.keyword_search.search(query, top_k=initial_k)

            logger.debug(f"向量检索: {len(vector_results)} 个结果")
            logger.debug(f"关键词检索: {len(keyword_results)} 个结果")

            # 融合结果
            if self.fusion_method == 'rrf':
                results = self._rrf_fusion(vector_results, keyword_results)
            elif self.fusion_method == 'linear':
                results = self._linear_fusion(vector_results, keyword_results)
            else:
                logger.warning(f"未知的融合方法: {self.fusion_method}，使用 RRF")
                results = self._rrf_fusion(vector_results, keyword_results)

            # 智能去重（移除相似度过高的重复结果）
            results = self._deduplicate_results(results, similarity_threshold=0.9)

            # 如果启用重排序，使用Cross-Encoder重新排序
            if self.rerank_enabled and results:
                logger.debug(f"执行重排序: {len(results)} → {top_k}")
                results = self.reranker.rerank(
                    query=query,
                    results=results[:initial_k],
                    top_k=top_k
                )
            else:
                # 返回 top-k
                results = results[:top_k]

            logger.debug(f"最终返回 {len(results)} 个结果")
            return results

        except Exception as e:
            logger.error(f"混合检索失败: {e}")
            return []

    def _rrf_fusion(self, vector_results: List[Dict], keyword_results: List[Dict]) -> List[Dict]:
        """
        Reciprocal Rank Fusion (RRF) 融合

        Args:
            vector_results: 向量检索结果
            keyword_results: 关键词检索结果

        Returns:
            融合后的结果
        """
        # 计算 RRF 分数
        rrf_scores = {}

        # 向量检索结果
        for result in vector_results:
            chunk_id = result['chunk_id']
            rank = result['rank']
            rrf_score = 1.0 / (self.rrf_k + rank)

            if chunk_id not in rrf_scores:
                rrf_scores[chunk_id] = {
                    'doc_id': result['doc_id'],
                    'chunk_id': chunk_id,
                    'content': result['content'],
                    'vector_score': result['score'],
                    'keyword_score': 0,
                    'rrf_score': 0
                }

            rrf_scores[chunk_id]['rrf_score'] += rrf_score * self.vector_weight

        # 关键词检索结果
        for result in keyword_results:
            chunk_id = result['chunk_id']
            rank = result['rank']
            rrf_score = 1.0 / (self.rrf_k + rank)

            if chunk_id not in rrf_scores:
                rrf_scores[chunk_id] = {
                    'doc_id': result['doc_id'],
                    'chunk_id': chunk_id,
                    'content': result['content'],
                    'vector_score': 0,
                    'keyword_score': result['score'],
                    'rrf_score': 0
                }
            else:
                rrf_scores[chunk_id]['keyword_score'] = result['score']

            rrf_scores[chunk_id]['rrf_score'] += rrf_score * self.keyword_weight

        # 排序
        sorted_results = sorted(
            rrf_scores.values(),
            key=lambda x: x['rrf_score'],
            reverse=True
        )

        # 格式化结果
        final_results = []
        for i, result in enumerate(sorted_results, 1):
            final_results.append({
                'doc_id': result['doc_id'],
                'chunk_id': result['chunk_id'],
                'content': result['content'],
                'score': result['rrf_score'],
                'vector_score': result['vector_score'],
                'keyword_score': result['keyword_score'],
                'rank': i
            })

        return final_results

    def _linear_fusion(self, vector_results: List[Dict], keyword_results: List[Dict]) -> List[Dict]:
        """
        线性加权融合

        Args:
            vector_results: 向量检索结果
            keyword_results: 关键词检索结果

        Returns:
            融合后的结果
        """
        combined_scores = {}

        # 向量检索结果
        for result in vector_results:
            chunk_id = result['chunk_id']
            if chunk_id not in combined_scores:
                combined_scores[chunk_id] = {
                    'doc_id': result['doc_id'],
                    'chunk_id': chunk_id,
                    'content': result['content'],
                    'score': 0
                }
            combined_scores[chunk_id]['score'] += result['score'] * self.vector_weight

        # 关键词检索结果（需要归一化）
        max_keyword_score = max((r['score'] for r in keyword_results), default=1)

        for result in keyword_results:
            chunk_id = result['chunk_id']
            normalized_score = result['score'] / max_keyword_score

            if chunk_id not in combined_scores:
                combined_scores[chunk_id] = {
                    'doc_id': result['doc_id'],
                    'chunk_id': chunk_id,
                    'content': result['content'],
                    'score': 0
                }
            combined_scores[chunk_id]['score'] += normalized_score * self.keyword_weight

        # 排序
        sorted_results = sorted(
            combined_scores.values(),
            key=lambda x: x['score'],
            reverse=True
        )

        # 添加排名
        for i, result in enumerate(sorted_results, 1):
            result['rank'] = i

        return sorted_results

    def _deduplicate_results(
        self,
        results: List[Dict],
        similarity_threshold: float = 0.9
    ) -> List[Dict]:
        """
        智能去重：移除内容高度相似的重复结果

        Args:
            results: 检索结果列表
            similarity_threshold: 相似度阈值

        Returns:
            去重后的结果
        """
        if not results or len(results) <= 1:
            return results

        deduplicated = []
        seen_contents = []

        for result in results:
            content = result.get('content', '')

            # 检查是否与已有结果过于相似
            is_duplicate = False
            for seen_content in seen_contents:
                similarity = self._compute_text_similarity(content, seen_content)
                if similarity > similarity_threshold:
                    is_duplicate = True
                    logger.debug(f"检测到重复结果 (相似度: {similarity:.2f})")
                    break

            if not is_duplicate:
                deduplicated.append(result)
                seen_contents.append(content)

        logger.debug(f"去重: {len(results)} → {len(deduplicated)}")
        return deduplicated

    def _compute_text_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度（简单基于字符重叠）

        Args:
            text1: 文本1
            text2: 文本2

        Returns:
            相似度 [0, 1]
        """
        # 简单方法：Jaccard相似度
        set1 = set(text1)
        set2 = set(text2)

        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def _diversity_aware_ranking(
        self,
        results: List[Dict],
        diversity_weight: float = 0.3
    ) -> List[Dict]:
        """
        多样性感知排序：在相关性和多样性之间平衡

        Args:
            results: 检索结果
            diversity_weight: 多样性权重

        Returns:
            重排序后的结果
        """
        if not results or len(results) <= 1:
            return results

        # MMR (Maximal Marginal Relevance) 算法
        selected = []
        remaining = results.copy()

        # 先选择分数最高的
        selected.append(remaining.pop(0))

        while remaining and len(selected) < len(results):
            best_idx = 0
            best_score = -float('inf')

            for i, candidate in enumerate(remaining):
                # 计算与已选结果的平均相似度
                avg_similarity = np.mean([
                    self._compute_text_similarity(
                        candidate['content'],
                        s['content']
                    )
                    for s in selected
                ])

                # MMR分数 = 相关性 - λ * 平均相似度
                mmr_score = (
                    candidate['score'] * (1 - diversity_weight) -
                    avg_similarity * diversity_weight
                )

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = i

            selected.append(remaining.pop(best_idx))

        # 更新排名
        for i, result in enumerate(selected, 1):
            result['rank'] = i

        return selected

    def get_info(self) -> dict:
        """获取检索引擎信息"""
        return {
            'vector_weight': self.vector_weight,
            'keyword_weight': self.keyword_weight,
            'fusion_method': self.fusion_method,
            'rrf_k': self.rrf_k,
            'reranker': self.reranker.get_info()
        }
