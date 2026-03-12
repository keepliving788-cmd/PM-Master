"""
索引管理器 - 负责构建和管理索引
"""
from typing import Dict, List
from pathlib import Path
import json
import time
from datetime import datetime
from loguru import logger
from tqdm import tqdm

from .feishu_client import FeishuClient
from .doc_processor import DocumentProcessor
from ..storage.vector_store import VectorStore
from ..storage.doc_store import DocumentStore


class IndexManager:
    """索引管理器"""

    def __init__(self, config):
        """
        初始化索引管理器

        Args:
            config: 配置对象
        """
        self.config = config

        # 初始化飞书客户端
        self.feishu_client = FeishuClient(
            app_id=config.feishu['app_id'],
            app_secret=config.feishu['app_secret']
        )

        # 初始化文档处理器
        self.doc_processor = DocumentProcessor(config)

        # 初始化存储
        self.vector_store = VectorStore(config)
        self.doc_store = DocumentStore(config)

        logger.info("索引管理器初始化完成")

    def build_full_index(self, force: bool = False) -> Dict:
        """
        构建全量索引

        Args:
            force: 是否强制重建

        Returns:
            构建结果统计
        """
        start_time = time.time()

        # 如果强制重建，清空现有索引
        if force:
            logger.warning("强制重建索引，清空现有数据")
            self.vector_store.clear()
            self.doc_store.clear()

        # 获取知识空间 ID
        space_id = self.config.feishu['wiki_space_id']

        # 遍历所有节点
        logger.info("开始遍历知识空间节点...")
        nodes = self.feishu_client.traverse_wiki_space(space_id)

        # 过滤文档节点
        doc_nodes = [
            node for node in nodes
            if node['obj_type'] in ['docx', 'doc', 'wiki']
        ]

        logger.info(f"找到 {len(doc_nodes)} 个文档节点")

        # 处理文档
        stats = {
            'total_docs': 0,
            'new_docs': 0,
            'updated_docs': 0,
            'failed_docs': 0,
            'total_chunks': 0
        }

        for node in tqdm(doc_nodes, desc="处理文档"):
            try:
                # 检查是否已存在
                existing_doc = self.doc_store.get_document(node['obj_token'])

                # 获取文档内容
                doc_content = self.feishu_client.get_document_content(
                    doc_token=node['obj_token'],
                    doc_type=node['obj_type']
                )

                if not doc_content:
                    logger.warning(f"无法获取文档内容: {node['obj_token']}")
                    stats['failed_docs'] += 1
                    continue

                # 处理文档
                processed_doc = self.doc_processor.process_document(doc_content)

                # 保存到文档存储
                self.doc_store.save_document(processed_doc)

                # 添加到向量存储
                chunks = processed_doc['chunks']
                self.vector_store.add_documents(chunks)

                # 更新统计
                stats['total_docs'] += 1
                stats['total_chunks'] += len(chunks)

                if existing_doc:
                    stats['updated_docs'] += 1
                else:
                    stats['new_docs'] += 1

                logger.debug(f"处理完成: {doc_content['title']}")

            except Exception as e:
                logger.error(f"处理文档失败 {node['obj_token']}: {e}")
                stats['failed_docs'] += 1

        # 持久化存储
        self.vector_store.persist()

        # 保存索引元数据
        self._save_index_metadata({
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'space_id': space_id,
            'stats': stats
        })

        elapsed_time = time.time() - start_time
        stats['elapsed_time'] = elapsed_time

        logger.success(f"全量索引构建完成，耗时 {elapsed_time:.2f} 秒")

        return stats

    def build_incremental_index(self) -> Dict:
        """
        构建增量索引

        Returns:
            构建结果统计
        """
        start_time = time.time()

        # 获取上次索引时间
        metadata = self._load_index_metadata()
        last_updated = metadata.get('created_at') if metadata else None

        logger.info(f"上次索引时间: {last_updated}")

        # 获取更新的文档
        space_id = self.config.feishu['wiki_space_id']
        nodes = self.feishu_client.traverse_wiki_space(space_id)

        doc_nodes = [
            node for node in nodes
            if node['obj_type'] in ['docx', 'doc', 'wiki']
        ]

        stats = {
            'total_docs': 0,
            'new_docs': 0,
            'updated_docs': 0,
            'failed_docs': 0
        }

        for node in tqdm(doc_nodes, desc="增量更新"):
            try:
                # 检查是否需要更新
                existing_doc = self.doc_store.get_document(node['obj_token'])

                doc_content = self.feishu_client.get_document_content(
                    doc_token=node['obj_token'],
                    doc_type=node['obj_type']
                )

                if not doc_content:
                    continue

                # 判断是否需要更新
                if existing_doc:
                    if doc_content['updated_at'] <= existing_doc['updated_at']:
                        continue  # 跳过未更新的文档

                # 处理并保存
                processed_doc = self.doc_processor.process_document(doc_content)
                self.doc_store.save_document(processed_doc)

                # 更新向量存储
                if existing_doc:
                    self.vector_store.delete_document(node['obj_token'])
                    stats['updated_docs'] += 1
                else:
                    stats['new_docs'] += 1

                chunks = processed_doc['chunks']
                self.vector_store.add_documents(chunks)

                stats['total_docs'] += 1

            except Exception as e:
                logger.error(f"增量更新失败 {node['obj_token']}: {e}")
                stats['failed_docs'] += 1

        self.vector_store.persist()

        elapsed_time = time.time() - start_time
        stats['elapsed_time'] = elapsed_time

        logger.success(f"增量索引更新完成，耗时 {elapsed_time:.2f} 秒")

        return stats

    def sync(self) -> Dict:
        """
        同步知识库（增量更新的别名）

        Returns:
            同步结果
        """
        result = self.build_incremental_index()
        return {
            'added': result['new_docs'],
            'updated': result['updated_docs'],
            'deleted': 0  # 暂不支持删除检测
        }

    def _save_index_metadata(self, metadata: Dict):
        """保存索引元数据"""
        metadata_path = Path(self.config.storage['data_dir']) / 'index_metadata.json'
        metadata_path.parent.mkdir(parents=True, exist_ok=True)

        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def _load_index_metadata(self) -> Dict:
        """加载索引元数据"""
        metadata_path = Path(self.config.storage['data_dir']) / 'index_metadata.json'

        if not metadata_path.exists():
            return {}

        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
