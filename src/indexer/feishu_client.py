"""
飞书 API 客户端
"""
from typing import List, Dict, Optional
import lark_oapi as lark
from lark_oapi.api.wiki.v2 import *
from lark_oapi.api.docx.v1 import *
from loguru import logger
from datetime import datetime


class FeishuClient:
    """飞书知识库客户端"""

    def __init__(self, app_id: str, app_secret: str):
        """
        初始化客户端

        Args:
            app_id: 飞书应用 ID
            app_secret: 飞书应用密钥
        """
        self.client = lark.Client.builder() \
            .app_id(app_id) \
            .app_secret(app_secret) \
            .build()

        logger.info("飞书客户端初始化成功")

    def list_wiki_nodes(self, space_id: str, parent_node_token: Optional[str] = None) -> List[Dict]:
        """
        获取知识空间的节点列表

        Args:
            space_id: 知识空间 ID
            parent_node_token: 父节点 token（可选）

        Returns:
            节点列表
        """
        try:
            request = ListSpaceNodeRequest.builder() \
                .space_id(space_id) \
                .page_size(100) \
                .build()

            if parent_node_token:
                request.parent_node_token = parent_node_token

            response = self.client.wiki.v2.space_node.list(request)

            if not response.success():
                logger.error(f"获取节点列表失败: {response.msg}")
                return []

            nodes = []
            for item in response.data.items:
                nodes.append({
                    'node_token': item.node_token,
                    'obj_token': item.obj_token,
                    'obj_type': item.obj_type,
                    'parent_node_token': item.parent_node_token,
                    'node_type': item.node_type,
                    'origin_node_token': item.origin_node_token,
                    'has_child': item.has_child
                })

            logger.info(f"获取到 {len(nodes)} 个节点")
            return nodes

        except Exception as e:
            logger.error(f"获取节点列表异常: {e}")
            return []

    def get_wiki_node_info(self, space_id: str, node_token: str) -> Optional[Dict]:
        """
        获取节点详细信息

        Args:
            space_id: 知识空间 ID
            node_token: 节点 token

        Returns:
            节点信息
        """
        try:
            # 先获取节点基本信息
            request = GetSpaceNodeRequest.builder() \
                .space_id(space_id) \
                .node_token(node_token) \
                .build()

            response = self.client.wiki.v2.space_node.get(request)

            if not response.success():
                logger.error(f"获取节点信息失败: {response.msg}")
                return None

            node = response.data.node

            return {
                'node_token': node.node_token,
                'obj_token': node.obj_token,
                'obj_type': node.obj_type,
                'title': node.title,
                'owner_id': node.owner_id,
                'creator_id': node.creator_id,
                'has_child': node.has_child
            }

        except Exception as e:
            logger.error(f"获取节点信息异常: {e}")
            return None

    def get_document_content(self, doc_token: str, doc_type: str = 'docx') -> Optional[Dict]:
        """
        获取文档内容

        Args:
            doc_token: 文档 token
            doc_type: 文档类型 (docx, doc, wiki)

        Returns:
            文档内容
        """
        try:
            if doc_type == 'docx':
                return self._get_docx_content(doc_token)
            elif doc_type == 'doc':
                return self._get_doc_content(doc_token)
            elif doc_type == 'wiki':
                return self._get_wiki_content(doc_token)
            else:
                logger.warning(f"不支持的文档类型: {doc_type}")
                return None

        except Exception as e:
            logger.error(f"获取文档内容异常: {e}")
            return None

    def _get_docx_content(self, doc_token: str) -> Optional[Dict]:
        """获取新版文档内容"""
        try:
            # 获取文档元数据
            meta_request = GetDocumentRequest.builder() \
                .document_id(doc_token) \
                .build()

            meta_response = self.client.docx.v1.document.get(meta_request)

            if not meta_response.success():
                logger.error(f"获取文档元数据失败: {meta_response.msg}")
                return None

            doc = meta_response.data.document

            # 获取文档原始内容
            raw_request = RawContentDocumentRequest.builder() \
                .document_id(doc_token) \
                .build()

            raw_response = self.client.docx.v1.document.raw_content(raw_request)

            if not raw_response.success():
                logger.error(f"获取文档内容失败: {raw_response.msg}")
                return None

            content = raw_response.data.content

            return {
                'doc_token': doc_token,
                'doc_type': 'docx',
                'title': doc.title,
                'content': content,
                'created_at': datetime.fromtimestamp(int(doc.create_time)),
                'updated_at': datetime.fromtimestamp(int(doc.update_time)),
                'owner_id': doc.owner_id
            }

        except Exception as e:
            logger.error(f"获取新版文档内容异常: {e}")
            return None

    def _get_doc_content(self, doc_token: str) -> Optional[Dict]:
        """获取旧版文档内容（需要另外的 API）"""
        # 旧版 doc API 需要另外实现
        logger.warning("旧版文档暂不支持，请转换为新版文档")
        return None

    def _get_wiki_content(self, wiki_token: str) -> Optional[Dict]:
        """获取 Wiki 内容"""
        # Wiki API 实现
        logger.warning("Wiki 文档暂不支持")
        return None

    def traverse_wiki_space(self, space_id: str) -> List[Dict]:
        """
        遍历知识空间所有节点

        Args:
            space_id: 知识空间 ID

        Returns:
            所有节点列表
        """
        all_nodes = []

        def traverse(parent_token=None):
            nodes = self.list_wiki_nodes(space_id, parent_token)

            for node in nodes:
                all_nodes.append(node)

                # 如果有子节点，递归遍历
                if node.get('has_child'):
                    traverse(node['node_token'])

        logger.info(f"开始遍历知识空间: {space_id}")
        traverse()
        logger.info(f"遍历完成，共 {len(all_nodes)} 个节点")

        return all_nodes
