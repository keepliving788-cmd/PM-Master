"""
Cross-Encoder重排序模块
用于对初排序结果进行精细打分，提升Top-K精度
"""
from typing import List, Dict
from sentence_transformers import CrossEncoder
from loguru import logger
import numpy as np


class Reranker:
    """Cross-Encoder重排序器"""

    def __init__(self, config):
        """
        初始化Reranker

        Args:
            config: 配置对象
        """
        self.config = config
        self.enabled = config.retrieval['rerank']['enabled']

        if not self.enabled:
            logger.info("重排序功能未启用")
            self.model = None
            return

        self.model_name = config.retrieval['rerank']['model']
        self.top_k = config.retrieval['rerank']['top_k']
        self.batch_size = config.retrieval['rerank'].get('batch_size', 16)
        self.initial_top_k = config.retrieval['rerank'].get('initial_top_k', 30)

        logger.info(f"加载Reranker模型: {self.model_name}")

        try:
            # 加载Cross-Encoder模型
            self.model = CrossEncoder(
                self.model_name,
                max_length=512
            )
            logger.success(f"Reranker模型加载成功")
            logger.info(f"  - 模型: {self.model_name}")
            logger.info(f"  - 初排序获取: {self.initial_top_k} 条")
            logger.info(f"  - 重排序返回: {self.top_k} 条")

        except Exception as e:
            logger.error(f"Reranker模型加载失败: {e}")
            logger.warning("重排序功能将被禁用")
            self.enabled = False
            self.model = None

    def rerank(
        self,
        query: str,
        results: List[Dict],
        top_k: int = None
    ) -> List[Dict]:
        """
        对检索结果进行重排序

        Args:
            query: 查询文本
            results: 初排序结果列表
            top_k: 返回结果数量（可选）

        Returns:
            重排序后的结果列表
        """
        if not self.enabled or self.model is None:
            return results[:top_k] if top_k else results

        if not results:
            return []

        if top_k is None:
            top_k = self.top_k

        logger.debug(f"重排序 {len(results)} 个结果...")

        try:
            # 准备query-document对
            pairs = [
                [query, result['content']]
                for result in results
            ]

            # 使用Cross-Encoder打分
            scores = self.model.predict(
                pairs,
                batch_size=self.batch_size,
                show_progress_bar=False
            )

            # 更新分数
            for i, result in enumerate(results):
                result['rerank_score'] = float(scores[i])
                result['original_score'] = result.get('score', 0.0)

            # 按重排序分数排序
            reranked_results = sorted(
                results,
                key=lambda x: x['rerank_score'],
                reverse=True
            )

            # 更新排名
            for i, result in enumerate(reranked_results, 1):
                result['rank'] = i
                result['score'] = result['rerank_score']  # 使用rerank分数作为最终分数

            logger.debug(f"重排序完成，返回Top-{top_k}")

            # 返回Top-K
            return reranked_results[:top_k]

        except Exception as e:
            logger.error(f"重排序失败: {e}")
            # 失败时返回原始结果
            return results[:top_k]

    def score_pairs(
        self,
        query: str,
        documents: List[str]
    ) -> np.ndarray:
        """
        直接对query-document对打分

        Args:
            query: 查询文本
            documents: 文档列表

        Returns:
            分数数组
        """
        if not self.enabled or self.model is None:
            return np.zeros(len(documents))

        pairs = [[query, doc] for doc in documents]

        scores = self.model.predict(
            pairs,
            batch_size=self.batch_size,
            show_progress_bar=False
        )

        return scores

    def is_enabled(self) -> bool:
        """检查重排序是否启用"""
        return self.enabled and self.model is not None

    def get_info(self) -> dict:
        """获取重排序器信息"""
        if not self.enabled:
            return {'enabled': False}

        return {
            'enabled': True,
            'model_name': self.model_name,
            'top_k': self.top_k,
            'initial_top_k': self.initial_top_k,
            'batch_size': self.batch_size
        }
