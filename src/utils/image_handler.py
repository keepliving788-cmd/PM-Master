#!/usr/bin/env python3
"""
图片处理模块 - 实时获取和理解飞书文档中的图片
"""
import os
import re
import base64
import time
from typing import List, Dict, Optional, Tuple
from pathlib import Path

import lark_oapi as lark
from lark_oapi.api.docx.v1 import *
from lark_oapi.api.drive.v1 import *
from loguru import logger


class ImageHandler:
    """飞书图片处理器 - 实时获取和理解图片内容"""

    def __init__(self):
        """初始化飞书客户端"""
        self.client = lark.Client.builder() \
            .app_id(os.environ.get('FEISHU_APP_ID')) \
            .app_secret(os.environ.get('FEISHU_APP_SECRET')) \
            .build()

        # 临时图片缓存（会话级别）
        self.image_cache = {}

        logger.info("图片处理器初始化完成")

    def extract_image_references(self, text: str) -> List[str]:
        """
        从文本中提取图片引用

        Args:
            text: 文档文本内容

        Returns:
            图片文件名列表
        """
        # 匹配各种图片引用格式
        patterns = [
            r'([a-zA-Z0-9_-]+\.png)',
            r'([a-zA-Z0-9_-]+\.jpg)',
            r'([a-zA-Z0-9_-]+\.jpeg)',
            r'(img_v3_[a-zA-Z0-9_-]+\.png)',
        ]

        images = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            images.extend(matches)

        # 去重
        images = list(set(images))

        if images:
            logger.debug(f"从文本中提取到 {len(images)} 个图片引用")

        return images

    def get_document_images(self, doc_token: str) -> List[Dict]:
        """
        获取文档中的所有图片信息

        Args:
            doc_token: 文档 token

        Returns:
            图片信息列表，每个包含 token 和上下文
        """
        try:
            # 获取文档完整结构
            request = GetDocumentRequest.builder() \
                .document_id(doc_token) \
                .build()

            response = self.client.docx.v1.document.get(request)

            if not response.success():
                logger.warning(f"获取文档结构失败: {response.msg}")
                return []

            # 遍历文档块，找到图片块
            images = []
            if hasattr(response.data, 'document') and hasattr(response.data.document, 'body'):
                blocks = response.data.document.body.blocks if hasattr(response.data.document.body, 'blocks') else []

                for block in blocks:
                    if hasattr(block, 'block_type') and block.block_type == 27:  # 27 是图片类型
                        if hasattr(block, 'image') and hasattr(block.image, 'token'):
                            images.append({
                                'token': block.image.token,
                                'context': self._extract_context(blocks, block)
                            })

            logger.info(f"文档 {doc_token} 包含 {len(images)} 张图片")
            return images

        except Exception as e:
            logger.error(f"获取文档图片失败: {e}")
            return []

    def _extract_context(self, blocks: List, image_block) -> str:
        """提取图片周围的上下文（前后文本）"""
        # 简化实现：返回图片前的文本作为上下文
        try:
            block_index = blocks.index(image_block)
            context_blocks = blocks[max(0, block_index-2):block_index]

            context_text = []
            for block in context_blocks:
                if hasattr(block, 'text') and hasattr(block.text, 'elements'):
                    for element in block.text.elements:
                        if hasattr(element, 'text_run') and hasattr(element.text_run, 'content'):
                            context_text.append(element.text_run.content)

            return ' '.join(context_text)[:200]  # 限制长度
        except:
            return ""

    def download_image(self, image_token: str) -> Optional[bytes]:
        """
        下载图片数据

        Args:
            image_token: 图片 token

        Returns:
            图片二进制数据，失败返回 None
        """
        # 检查缓存
        if image_token in self.image_cache:
            logger.debug(f"从缓存获取图片: {image_token}")
            return self.image_cache[image_token]

        try:
            # 下载图片
            request = DownloadMediaRequest.builder() \
                .file_token(image_token) \
                .build()

            response = self.client.drive.v1.media.download(request)

            if response.success():
                image_data = response.file.read()

                # 缓存图片（会话级别）
                self.image_cache[image_token] = image_data

                logger.info(f"成功下载图片: {image_token} ({len(image_data)} bytes)")
                return image_data
            else:
                logger.warning(f"下载图片失败: {response.msg}")
                return None

        except Exception as e:
            logger.error(f"下载图片异常: {e}")
            return None

    def clear_cache(self):
        """清空图片缓存"""
        self.image_cache.clear()
        logger.debug("图片缓存已清空")


class ClaudeImageUnderstanding:
    """Claude 图片理解器"""

    def __init__(self):
        """初始化 Anthropic 客户端"""
        # 检查是否有 API key
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')

        if not self.api_key:
            logger.warning("未设置 ANTHROPIC_API_KEY，图片理解功能将不可用")
            self.client = None
        else:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info("Claude 图片理解器初始化完成")
            except ImportError:
                logger.error("anthropic 包未安装，请运行: pip install anthropic")
                self.client = None

    def understand_image(
        self,
        image_data: bytes,
        context: str = "",
        media_type: str = "image/png"
    ) -> Optional[str]:
        """
        使用 Claude 理解图片内容

        Args:
            image_data: 图片二进制数据
            context: 图片上下文（周围的文字）
            media_type: 图片类型

        Returns:
            图片内容描述，失败返回 None
        """
        if not self.client:
            logger.warning("Claude 客户端未初始化，跳过图片理解")
            return None

        try:
            # 转换为 base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # 构建提示词
            prompt = self._build_prompt(context)

            # 调用 Claude API
            start_time = time.time()

            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=300,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_base64,
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            )

            elapsed = time.time() - start_time

            description = response.content[0].text
            logger.info(f"图片理解完成 (耗时 {elapsed:.2f}秒)")
            logger.debug(f"描述: {description[:100]}...")

            return description

        except Exception as e:
            logger.error(f"图片理解失败: {e}")
            return None

    def _build_prompt(self, context: str) -> str:
        """构建图片理解提示词"""
        base_prompt = """请简洁描述这张图片的内容（50字以内），包括：
1. 图片类型（产品图/截图/流程图/架构图/表格/数据图等）
2. 主要内容和关键信息点
3. 如果有文字，提取关键文字"""

        if context:
            base_prompt = f"上下文：{context}\n\n{base_prompt}"

        return base_prompt

    def batch_understand(
        self,
        images: List[Tuple[bytes, str]]
    ) -> List[Optional[str]]:
        """
        批量理解多张图片

        Args:
            images: [(图片数据, 上下文), ...]

        Returns:
            描述列表
        """
        descriptions = []

        for i, (image_data, context) in enumerate(images, 1):
            logger.info(f"处理图片 {i}/{len(images)}")
            desc = self.understand_image(image_data, context)
            descriptions.append(desc)

            # 避免请求过快
            if i < len(images):
                time.sleep(0.5)

        return descriptions


# 全局单例
_image_handler = None
_claude_understanding = None


def get_image_handler() -> ImageHandler:
    """获取图片处理器单例"""
    global _image_handler
    if _image_handler is None:
        _image_handler = ImageHandler()
    return _image_handler


def get_claude_understanding() -> ClaudeImageUnderstanding:
    """获取 Claude 图片理解器单例"""
    global _claude_understanding
    if _claude_understanding is None:
        _claude_understanding = ClaudeImageUnderstanding()
    return _claude_understanding
