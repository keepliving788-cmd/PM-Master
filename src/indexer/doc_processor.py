"""
文档处理器 - 负责文档分块和处理
升级版：使用智能分块器
"""
from typing import Dict, List
import re
from bs4 import BeautifulSoup
from loguru import logger
import sys
from pathlib import Path

# 添加utils到路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.smart_chunker import SmartChunker


class DocumentProcessor:
    """文档处理器（升级版）"""

    def __init__(self, config):
        """
        初始化文档处理器

        Args:
            config: 配置对象
        """
        self.config = config
        self.chunk_size = config.indexing['chunking']['chunk_size']
        self.chunk_overlap = config.indexing['chunking']['chunk_overlap']
        self.separators = config.indexing['chunking']['separators']

        # 初始化智能分块器
        self.smart_chunker = SmartChunker(config)
        logger.info("文档处理器初始化完成（智能分块模式）")

    def process_document(self, doc: Dict) -> Dict:
        """
        处理文档（使用智能分块）

        Args:
            doc: 原始文档

        Returns:
            处理后的文档
        """
        # 清洗内容
        cleaned_content = self._clean_content(doc['content'])

        # 使用智能分块器
        chunks = self.smart_chunker.chunk_document(
            text=cleaned_content,
            doc_id=doc['doc_token'],
            title=doc['title'],
            metadata={
                'doc_type': doc['doc_type'],
                'created_at': doc['created_at'],
                'updated_at': doc['updated_at'],
                'owner_id': doc.get('owner_id')
            }
        )

        # 构建处理后的文档
        processed_doc = {
            'doc_id': doc['doc_token'],
            'doc_type': doc['doc_type'],
            'title': doc['title'],
            'content': cleaned_content,
            'created_at': doc['created_at'],
            'updated_at': doc['updated_at'],
            'owner_id': doc.get('owner_id'),
            'chunks': chunks,
            'metadata': {
                'chunk_count': len(chunks),
                'char_count': len(cleaned_content),
                'word_count': len(cleaned_content.split()),
                'chunking_strategy': 'smart'
            }
        }

        logger.debug(f"文档处理完成: {doc['title']}, {len(chunks)} 个块")

        return processed_doc

    def _clean_content(self, content: str) -> str:
        """
        清洗文档内容

        Args:
            content: 原始内容

        Returns:
            清洗后的内容
        """
        # 移除 HTML 标签
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()

        # 移除多余空白
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)

        # 移除特殊字符
        text = text.strip()

        return text

    def _chunk_text(self, text: str, doc_id: str, title: str) -> List[Dict]:
        """
        分块文本

        Args:
            text: 文本内容
            doc_id: 文档 ID
            title: 文档标题

        Returns:
            文本块列表
        """
        strategy = self.config.indexing['chunking']['strategy']

        if strategy == 'fixed':
            return self._chunk_fixed(text, doc_id, title)
        elif strategy == 'recursive':
            return self._chunk_recursive(text, doc_id, title)
        elif strategy == 'semantic':
            return self._chunk_semantic(text, doc_id, title)
        else:
            logger.warning(f"未知的分块策略: {strategy}，使用默认策略")
            return self._chunk_recursive(text, doc_id, title)

    def _chunk_fixed(self, text: str, doc_id: str, title: str) -> List[Dict]:
        """固定大小分块"""
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]

            if chunk_text.strip():
                chunks.append({
                    'doc_id': doc_id,
                    'chunk_id': f"{doc_id}_{len(chunks)}",
                    'title': title,
                    'content': chunk_text,
                    'chunk_index': len(chunks),
                    'start_pos': start,
                    'end_pos': end
                })

            start = end - self.chunk_overlap

        return chunks

    def _chunk_recursive(self, text: str, doc_id: str, title: str) -> List[Dict]:
        """递归分块（按分隔符优先级）"""
        chunks = []

        def split_text(text: str, separators: List[str]) -> List[str]:
            """递归分割文本"""
            if not separators or len(text) <= self.chunk_size:
                return [text]

            separator = separators[0]
            splits = text.split(separator)

            result = []
            current_chunk = ""

            for split in splits:
                if len(current_chunk) + len(split) + len(separator) <= self.chunk_size:
                    if current_chunk:
                        current_chunk += separator
                    current_chunk += split
                else:
                    if current_chunk:
                        result.append(current_chunk)

                    if len(split) > self.chunk_size:
                        # 递归处理过长的片段
                        result.extend(split_text(split, separators[1:]))
                    else:
                        current_chunk = split

            if current_chunk:
                result.append(current_chunk)

            return result

        # 分割文本
        text_chunks = split_text(text, self.separators)

        # 添加重叠
        for i, chunk_text in enumerate(text_chunks):
            if not chunk_text.strip():
                continue

            # 添加前文重叠
            if i > 0 and self.chunk_overlap > 0:
                prev_text = text_chunks[i - 1]
                overlap = prev_text[-self.chunk_overlap:]
                chunk_text = overlap + chunk_text

            chunks.append({
                'doc_id': doc_id,
                'chunk_id': f"{doc_id}_{i}",
                'title': title,
                'content': chunk_text.strip(),
                'chunk_index': i,
                'total_chunks': len(text_chunks)
            })

        return chunks

    def _chunk_semantic(self, text: str, doc_id: str, title: str) -> List[Dict]:
        """语义分块（基于段落和语义边界）"""
        # TODO: 实现基于语义的分块
        # 可以使用句子级别的 embedding 相似度来确定分块边界
        logger.warning("语义分块暂未实现，使用递归分块")
        return self._chunk_recursive(text, doc_id, title)
