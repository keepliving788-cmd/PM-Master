"""
文档存储 - 使用 JSON 文件存储
"""
from typing import Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime
from loguru import logger


class DocumentStore:
    """文档存储"""

    def __init__(self, config):
        """
        初始化文档存储

        Args:
            config: 配置对象
        """
        self.config = config

        # 创建存储目录
        self.storage_dir = Path(config.storage['processed_dir'])
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # 索引文件（文档 ID -> 文件路径映射）
        self.index_file = self.storage_dir / 'index.json'
        self.index = self._load_index()

        logger.info(f"文档存储初始化完成: {self.storage_dir}")

    def save_document(self, doc: Dict):
        """
        保存文档

        Args:
            doc: 文档数据
        """
        doc_id = doc['doc_id']
        doc_file = self.storage_dir / f"{doc_id}.json"

        # 添加保存时间
        doc['saved_at'] = datetime.now().isoformat()

        # 保存文档
        with open(doc_file, 'w', encoding='utf-8') as f:
            json.dump(doc, f, ensure_ascii=False, indent=2, default=str)

        # 更新索引
        self.index[doc_id] = {
            'file_path': str(doc_file),
            'title': doc['title'],
            'updated_at': doc['updated_at'].isoformat() if isinstance(doc['updated_at'], datetime) else doc['updated_at']
        }
        self._save_index()

        logger.debug(f"保存文档: {doc['title']}")

    def get_document(self, doc_id: str) -> Optional[Dict]:
        """
        获取文档

        Args:
            doc_id: 文档 ID

        Returns:
            文档数据，如果不存在返回 None
        """
        if doc_id not in self.index:
            return None

        doc_file = Path(self.index[doc_id]['file_path'])

        if not doc_file.exists():
            logger.warning(f"文档文件不存在: {doc_file}")
            return None

        with open(doc_file, 'r', encoding='utf-8') as f:
            doc = json.load(f)

        # 转换日期字符串为 datetime（如果需要）
        if isinstance(doc.get('created_at'), str):
            doc['created_at'] = datetime.fromisoformat(doc['created_at'])
        if isinstance(doc.get('updated_at'), str):
            doc['updated_at'] = datetime.fromisoformat(doc['updated_at'])

        return doc

    def list_documents(self) -> List[Dict]:
        """
        列出所有文档

        Returns:
            文档列表
        """
        documents = []

        for doc_id in self.index.keys():
            doc = self.get_document(doc_id)
            if doc:
                documents.append(doc)

        return documents

    def delete_document(self, doc_id: str):
        """
        删除文档

        Args:
            doc_id: 文档 ID
        """
        if doc_id not in self.index:
            return

        doc_file = Path(self.index[doc_id]['file_path'])

        if doc_file.exists():
            doc_file.unlink()

        del self.index[doc_id]
        self._save_index()

        logger.debug(f"删除文档: {doc_id}")

    def clear(self):
        """清空文档存储"""
        logger.warning("清空文档存储")

        # 删除所有文档文件
        for doc_id in list(self.index.keys()):
            self.delete_document(doc_id)

        self.index = {}
        self._save_index()

    def _load_index(self) -> Dict:
        """加载索引"""
        if not self.index_file.exists():
            return {}

        with open(self.index_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_index(self):
        """保存索引"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
