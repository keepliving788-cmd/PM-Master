"""
向量存储 - 使用 ChromaDB
"""
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from loguru import logger
from pathlib import Path


class VectorStore:
    """向量数据库"""

    def __init__(self, config):
        """
        初始化向量存储

        Args:
            config: 配置对象
        """
        self.config = config

        # 初始化 ChromaDB
        persist_dir = Path(config.storage['chromadb']['persist_directory'])
        persist_dir.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # 初始化 Embedding 模型
        model_name = config.indexing['embedding']['model_name']
        logger.info(f"加载 Embedding 模型: {model_name}")
        self.embedding_model = SentenceTransformer(model_name)

        # 获取或创建集合
        collection_name = config.storage['chromadb']['collection_name']
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        logger.info(f"向量存储初始化完成，集合: {collection_name}")

    def add_documents(self, chunks: List[Dict]):
        """
        添加文档块到向量存储

        Args:
            chunks: 文档块列表
        """
        if not chunks:
            return

        # 准备数据
        ids = [chunk['chunk_id'] for chunk in chunks]
        documents = [chunk['content'] for chunk in chunks]
        metadatas = [
            {
                'doc_id': chunk['doc_id'],
                'title': chunk['title'],
                'chunk_index': chunk['chunk_index']
            }
            for chunk in chunks
        ]

        # 计算 embeddings
        embeddings = self.embedding_model.encode(
            documents,
            batch_size=self.config.indexing['embedding']['batch_size'],
            show_progress_bar=False,
            normalize_embeddings=self.config.indexing['embedding']['normalize']
        ).tolist()

        # 添加到 ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        logger.debug(f"添加 {len(chunks)} 个文档块到向量存储")

    def query(self, query_text: str, n_results: int = 10) -> Dict:
        """
        查询向量存储

        Args:
            query_text: 查询文本
            n_results: 返回结果数量

        Returns:
            查询结果
        """
        # 计算查询向量
        query_embedding = self.embedding_model.encode(
            [query_text],
            normalize_embeddings=self.config.indexing['embedding']['normalize']
        ).tolist()

        # 查询
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )

        return results

    def delete_document(self, doc_id: str):
        """
        删除文档的所有块

        Args:
            doc_id: 文档 ID
        """
        # 查询文档的所有块
        results = self.collection.get(
            where={"doc_id": doc_id}
        )

        if results['ids']:
            self.collection.delete(ids=results['ids'])
            logger.debug(f"删除文档 {doc_id} 的 {len(results['ids'])} 个块")

    def clear(self):
        """清空向量存储"""
        logger.warning("清空向量存储")
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"}
        )

    def persist(self):
        """持久化（ChromaDB 自动持久化，此方法为兼容性保留）"""
        logger.debug("向量存储已自动持久化")

    def count(self) -> int:
        """获取文档块数量"""
        return self.collection.count()
