"""
智能文档分块器
- 识别标题层级结构
- 保留上下文信息
- 避免在句子中间截断
- 支持多种分块策略
"""
from typing import List, Dict, Tuple
import re
from loguru import logger


class SmartChunker:
    """智能文档分块器"""

    def __init__(self, config):
        """
        初始化分块器

        Args:
            config: 配置对象
        """
        self.config = config
        self.chunk_size = config.indexing['chunking']['chunk_size']
        self.chunk_overlap = config.indexing['chunking']['chunk_overlap']
        self.strategy = config.indexing['chunking'].get('strategy', 'recursive')

        logger.info(f"智能分块器初始化: {self.strategy}, size={self.chunk_size}")

    def chunk_document(
        self,
        text: str,
        doc_id: str,
        title: str,
        metadata: Dict = None
    ) -> List[Dict]:
        """
        智能分块文档

        Args:
            text: 文档文本
            doc_id: 文档ID
            title: 文档标题
            metadata: 文档元数据

        Returns:
            文档块列表
        """
        if not text or not text.strip():
            return []

        logger.debug(f"开始分块: {title} ({len(text)} 字符)")

        # 1. 解析文档结构
        structure = self._parse_structure(text)

        # 2. 基于结构进行分块
        if structure['has_headers']:
            chunks = self._chunk_by_structure(
                text,
                structure,
                doc_id,
                title
            )
        else:
            chunks = self._chunk_by_content(
                text,
                doc_id,
                title
            )

        # 3. 添加元数据
        for chunk in chunks:
            chunk['doc_title'] = title
            if metadata:
                chunk['doc_metadata'] = metadata

        logger.debug(f"分块完成: {len(chunks)} 个块")
        return chunks

    def _parse_structure(self, text: str) -> Dict:
        """
        解析文档结构

        识别标题、段落等结构元素

        Args:
            text: 文档文本

        Returns:
            结构信息
        """
        lines = text.split('\n')

        structure = {
            'has_headers': False,
            'headers': [],
            'sections': []
        }

        current_section = {
            'header': None,
            'level': 0,
            'content': [],
            'start_line': 0
        }

        for i, line in enumerate(lines):
            # 识别 Markdown 风格标题
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)

            if header_match:
                # 保存前一个section
                if current_section['content'] or current_section['header']:
                    current_section['content'] = '\n'.join(current_section['content'])
                    structure['sections'].append(current_section.copy())

                # 开始新section
                level = len(header_match.group(1))
                header_text = header_match.group(2).strip()

                structure['has_headers'] = True
                structure['headers'].append({
                    'level': level,
                    'text': header_text,
                    'line': i
                })

                current_section = {
                    'header': header_text,
                    'level': level,
                    'content': [],
                    'start_line': i + 1
                }

            else:
                # 普通内容
                current_section['content'].append(line)

        # 保存最后一个section
        if current_section['content'] or current_section['header']:
            current_section['content'] = '\n'.join(current_section['content'])
            structure['sections'].append(current_section)

        return structure

    def _chunk_by_structure(
        self,
        text: str,
        structure: Dict,
        doc_id: str,
        title: str
    ) -> List[Dict]:
        """
        基于文档结构分块

        保留标题层级信息，确保块的语义完整性

        Args:
            text: 文档文本
            structure: 文档结构
            doc_id: 文档ID
            title: 文档标题

        Returns:
            文档块列表
        """
        chunks = []
        header_stack = []  # 维护当前标题路径

        for section in structure['sections']:
            # 更新标题栈
            if section['header']:
                # 弹出比当前level大的标题
                while header_stack and header_stack[-1]['level'] >= section['level']:
                    header_stack.pop()

                # 加入当前标题
                header_stack.append({
                    'level': section['level'],
                    'text': section['header']
                })

            content = section['content'].strip()
            if not content:
                continue

            # 构建header路径
            header_path = [h['text'] for h in header_stack]

            # 如果section内容过长，需要进一步分块
            if len(content) > self.chunk_size:
                sub_chunks = self._split_long_content(content, self.chunk_size)

                for i, sub_content in enumerate(sub_chunks):
                    chunk = self._create_chunk(
                        doc_id=doc_id,
                        title=title,
                        content=sub_content,
                        headers=header_path,
                        chunk_index=len(chunks),
                        is_sub_chunk=(i > 0)
                    )
                    chunks.append(chunk)
            else:
                chunk = self._create_chunk(
                    doc_id=doc_id,
                    title=title,
                    content=content,
                    headers=header_path,
                    chunk_index=len(chunks)
                )
                chunks.append(chunk)

        return chunks

    def _chunk_by_content(
        self,
        text: str,
        doc_id: str,
        title: str
    ) -> List[Dict]:
        """
        基于内容分块（无明显结构时）

        使用智能分割策略，避免在句子中间截断

        Args:
            text: 文档文本
            doc_id: 文档ID
            title: 文档标题

        Returns:
            文档块列表
        """
        chunks = []

        # 分割成段落
        paragraphs = text.split('\n\n')
        current_chunk = ""
        current_paragraphs = []

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # 检查是否超出大小限制
            if len(current_chunk) + len(para) + 2 > self.chunk_size:
                # 保存当前块
                if current_chunk:
                    chunk = self._create_chunk(
                        doc_id=doc_id,
                        title=title,
                        content=current_chunk,
                        headers=[],
                        chunk_index=len(chunks)
                    )
                    chunks.append(chunk)

                # 如果单个段落就超长，需要按句子分割
                if len(para) > self.chunk_size:
                    sub_chunks = self._split_long_content(para, self.chunk_size)
                    for sub_content in sub_chunks:
                        chunk = self._create_chunk(
                            doc_id=doc_id,
                            title=title,
                            content=sub_content,
                            headers=[],
                            chunk_index=len(chunks)
                        )
                        chunks.append(chunk)
                    current_chunk = ""
                else:
                    current_chunk = para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para

        # 保存最后一块
        if current_chunk:
            chunk = self._create_chunk(
                doc_id=doc_id,
                title=title,
                content=current_chunk,
                headers=[],
                chunk_index=len(chunks)
            )
            chunks.append(chunk)

        return chunks

    def _split_long_content(
        self,
        content: str,
        max_size: int
    ) -> List[str]:
        """
        分割过长内容

        按句子边界智能分割，避免在句子中间截断

        Args:
            content: 内容文本
            max_size: 最大大小

        Returns:
            分割后的内容列表
        """
        # 按句子分割（中文和英文）
        sentence_separators = r'([。！？；.!?;])'
        sentences = re.split(sentence_separators, content)

        # 重组句子（包含标点）
        full_sentences = []
        for i in range(0, len(sentences) - 1, 2):
            sent = sentences[i] + (sentences[i + 1] if i + 1 < len(sentences) else '')
            if sent.strip():
                full_sentences.append(sent)

        # 如果最后一个元素不是标点，也加入
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            full_sentences.append(sentences[-1])

        # 组合句子成块
        chunks = []
        current_chunk = ""

        for sentence in full_sentences:
            if len(current_chunk) + len(sentence) > max_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    # 添加overlap（取最后一个句子的部分）
                    overlap_text = current_chunk[-self.chunk_overlap:] if self.chunk_overlap > 0 else ""
                    current_chunk = overlap_text + sentence
                else:
                    # 单个句子就超长，强制分割
                    chunks.append(sentence[:max_size])
                    current_chunk = sentence[max_size:]
            else:
                current_chunk += sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _create_chunk(
        self,
        doc_id: str,
        title: str,
        content: str,
        headers: List[str],
        chunk_index: int,
        is_sub_chunk: bool = False
    ) -> Dict:
        """
        创建文档块

        Args:
            doc_id: 文档ID
            title: 文档标题
            content: 块内容
            headers: 标题路径
            chunk_index: 块索引
            is_sub_chunk: 是否是子块

        Returns:
            文档块字典
        """
        chunk_id = f"{doc_id}_chunk{chunk_index:04d}"

        # 构建上下文前缀（用于提升检索效果）
        context_prefix = ""
        if headers:
            context_prefix = " > ".join(headers) + "\n\n"

        return {
            'chunk_id': chunk_id,
            'doc_id': doc_id,
            'doc_title': title,
            'content': content,
            'content_with_context': context_prefix + content,  # 包含上下文的内容
            'headers': headers,
            'chunk_index': chunk_index,
            'is_sub_chunk': is_sub_chunk,
            'char_count': len(content),
            'metadata': {
                'header_path': ' > '.join(headers) if headers else None,
                'has_headers': len(headers) > 0
            }
        }
