"""
高精度Embedding模块
支持多种中文优化的embedding模型
"""
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from loguru import logger
import torch


class HighPrecisionEmbedder:
    """高精度Embedding器"""

    def __init__(self, config):
        """
        初始化Embedder

        Args:
            config: 配置对象
        """
        self.config = config
        self.model_name = config.indexing['embedding']['model_name']
        self.batch_size = config.indexing['embedding']['batch_size']
        self.normalize = config.indexing['embedding']['normalize']
        self.device = config.indexing['embedding'].get('device', 'auto')

        logger.info(f"加载Embedding模型: {self.model_name}")

        # 自动选择设备
        if self.device == 'auto':
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            logger.info(f"自动选择设备: {self.device}")

        # 加载模型
        try:
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device
            )

            # 获取实际维度
            self.dimension = self.model.get_sentence_embedding_dimension()
            logger.success(f"模型加载成功: {self.model_name}")
            logger.info(f"  - 维度: {self.dimension}")
            logger.info(f"  - 设备: {self.device}")
            logger.info(f"  - 归一化: {self.normalize}")

        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            logger.warning("回退到默认模型: paraphrase-multilingual-MiniLM-L12-v2")
            self.model_name = "paraphrase-multilingual-MiniLM-L12-v2"
            self.model = SentenceTransformer(self.model_name, device=self.device)
            self.dimension = self.model.get_sentence_embedding_dimension()

    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = None,
        show_progress: bool = False,
        convert_to_numpy: bool = True
    ) -> np.ndarray:
        """
        编码文本为向量

        Args:
            texts: 单个文本或文本列表
            batch_size: 批处理大小
            show_progress: 是否显示进度条
            convert_to_numpy: 是否转换为numpy数组

        Returns:
            向量数组 shape=(n_texts, dimension)
        """
        if batch_size is None:
            batch_size = self.batch_size

        # 处理单个文本
        if isinstance(texts, str):
            texts = [texts]

        logger.debug(f"编码 {len(texts)} 个文本...")

        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=convert_to_numpy,
                normalize_embeddings=self.normalize
            )

            logger.debug(f"编码完成: shape={embeddings.shape}")
            return embeddings

        except Exception as e:
            logger.error(f"编码失败: {e}")
            # 返回零向量作为fallback
            return np.zeros((len(texts), self.dimension))

    def encode_query(self, query: str) -> np.ndarray:
        """
        编码单个查询（带query前缀优化）

        某些模型（如BGE）建议为查询添加前缀以提升效果

        Args:
            query: 查询文本

        Returns:
            查询向量
        """
        # 对于某些模型，添加查询前缀
        if 'bge' in self.model_name.lower():
            query = f"为这个句子生成表示以用于检索相关文章：{query}"

        return self.encode(query, show_progress=False)[0]

    def encode_documents(
        self,
        documents: List[str],
        show_progress: bool = True
    ) -> np.ndarray:
        """
        编码文档列表（用于构建索引）

        Args:
            documents: 文档文本列表
            show_progress: 是否显示进度

        Returns:
            文档向量数组
        """
        logger.info(f"编码 {len(documents)} 个文档...")

        # 对于某些模型，不需要文档前缀（或已在分块时添加）
        embeddings = self.encode(
            documents,
            show_progress=show_progress
        )

        return embeddings

    def get_dimension(self) -> int:
        """获取向量维度"""
        return self.dimension

    def get_model_info(self) -> dict:
        """获取模型信息"""
        return {
            'model_name': self.model_name,
            'dimension': self.dimension,
            'device': self.device,
            'normalize': self.normalize,
            'batch_size': self.batch_size
        }
