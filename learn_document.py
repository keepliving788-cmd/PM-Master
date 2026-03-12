#!/usr/bin/env python3
"""
从飞书获取单个文档内容
支持文档URL或文档ID
"""
import os
import sys
import re
from pathlib import Path

# 直接读取.env
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

import lark_oapi as lark
from lark_oapi.api.docx.v1 import *
from lark_oapi.api.wiki.v2 import *


def extract_doc_id(url_or_id: str) -> tuple:
    """
    从URL或ID提取文档ID和类型

    支持的格式：
    - https://xxx.feishu.cn/docx/xxxxx
    - https://xxx.feishu.cn/wiki/xxxxx
    - 直接的文档ID

    Returns:
        (doc_id, doc_type) 元组，doc_type 可以是 'docx', 'wiki', 'unknown'
    """
    # 如果是URL，提取ID
    if url_or_id.startswith('http'):
        # 匹配 /docx/xxxxx 或 /wiki/xxxxx
        match = re.search(r'/(docx|wiki|docs|doc)/([a-zA-Z0-9_-]+)', url_or_id)
        if match:
            doc_type = match.group(1)
            doc_id = match.group(2)
            # 统一 doc 类型
            if doc_type in ['docs', 'doc']:
                doc_type = 'docx'
            return doc_id, doc_type
        else:
            print(f"⚠️  无法从URL解析文档ID: {url_or_id}")
            return url_or_id, 'unknown'
    else:
        # 直接是ID，尝试所有类型
        return url_or_id, 'unknown'


def fetch_document(doc_id: str, doc_type: str = 'unknown') -> dict:
    """
    获取单个文档内容

    Args:
        doc_id: 文档ID
        doc_type: 文档类型 (docx/wiki/unknown)

    Returns:
        {
            'doc_id': str,
            'title': str,
            'content': str,
            'doc_type': str,
            'success': bool
        }
    """
    app_id = os.environ.get('FEISHU_APP_ID')
    app_secret = os.environ.get('FEISHU_APP_SECRET')

    if not app_id or not app_secret:
        return {
            'success': False,
            'error': '未配置飞书凭证 (FEISHU_APP_ID, FEISHU_APP_SECRET)'
        }

    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(app_secret) \
        .build()

    print(f"📄 获取文档: {doc_id} (类型: {doc_type})")

    # 如果知道类型，直接获取
    if doc_type == 'docx':
        result = _fetch_docx(client, doc_id)
        if result['success']:
            return result
    elif doc_type == 'wiki':
        result = _fetch_wiki(client, doc_id)
        if result['success']:
            return result

    # 如果类型未知或获取失败，尝试所有类型
    if doc_type == 'unknown' or not result.get('success'):
        print("   尝试所有文档类型...")

        # 尝试 docx
        result = _fetch_docx(client, doc_id)
        if result['success']:
            return result

        # 尝试 wiki
        result = _fetch_wiki(client, doc_id)
        if result['success']:
            return result

    return {
        'success': False,
        'error': '无法获取文档内容，请检查文档ID/URL是否正确，以及是否有访问权限'
    }


def _fetch_docx(client, doc_id: str) -> dict:
    """获取文档（docx类型）"""
    try:
        request = RawContentDocumentRequest.builder() \
            .document_id(doc_id) \
            .lang(0) \
            .build()

        response = client.docx.v1.document.raw_content(request)

        if response.success():
            print(f"   ✅ 成功获取 docx 文档 ({len(response.data.content)} 字符)")

            # 尝试获取文档标题
            title = _get_document_title(client, doc_id, 'docx')

            return {
                'success': True,
                'doc_id': doc_id,
                'doc_type': 'docx',
                'title': title or f"文档_{doc_id}",
                'content': response.data.content
            }
        else:
            return {'success': False, 'error': f'docx: {response.msg}'}

    except Exception as e:
        return {'success': False, 'error': f'docx exception: {str(e)}'}


def _fetch_wiki(client, doc_id: str) -> dict:
    """获取知识库文档（wiki类型）"""
    try:
        # Wiki节点需要通过不同的API
        request = GetNodeSpaceRequest.builder().token(doc_id).build()
        response = client.wiki.v2.space.get_node(request)

        if response.success():
            node = response.data.node

            # 获取实际的文档内容
            if node.obj_type in ['docx', 'doc']:
                return _fetch_docx(client, node.obj_token)
            else:
                return {
                    'success': False,
                    'error': f'不支持的wiki节点类型: {node.obj_type}'
                }
        else:
            return {'success': False, 'error': f'wiki: {response.msg}'}

    except Exception as e:
        return {'success': False, 'error': f'wiki exception: {str(e)}'}


def _get_document_title(client, doc_id: str, doc_type: str) -> str:
    """获取文档标题"""
    try:
        if doc_type == 'docx':
            request = GetDocumentRequest.builder() \
                .document_id(doc_id) \
                .build()

            response = client.docx.v1.document.get(request)

            if response.success():
                return response.data.document.title
    except:
        pass

    return None


def save_learned_content(doc_data: dict):
    """保存学习的文档内容"""
    # 创建目录
    Path('data/raw/learned').mkdir(parents=True, exist_ok=True)

    # 保存文档
    filename = f"learned_{doc_data['doc_id']}.txt"
    output_path = f"data/raw/learned/{filename}"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# {doc_data['title']}\n\n")
        f.write(doc_data['content'])

    print(f"\n✅ 文档已保存: {output_path}")
    print(f"   标题: {doc_data['title']}")
    print(f"   大小: {len(doc_data['content'])} 字符")

    return output_path


def main():
    if len(sys.argv) < 2:
        print("用法: python3 learn_document.py <文档URL或ID>")
        print("\n示例:")
        print("  python3 learn_document.py https://xxx.feishu.cn/docx/xxxxx")
        print("  python3 learn_document.py doxcnxxxxxx")
        sys.exit(1)

    url_or_id = sys.argv[1]

    print("=" * 70)
    print("📚 学习飞书文档")
    print("=" * 70)

    # 提取文档ID
    doc_id, doc_type = extract_doc_id(url_or_id)
    print(f"\n文档ID: {doc_id}")
    print(f"文档类型: {doc_type}")

    # 获取文档内容
    print("\n" + "-" * 70)
    result = fetch_document(doc_id, doc_type)

    if result['success']:
        # 保存内容
        output_path = save_learned_content(result)

        print("\n" + "=" * 70)
        print("✅ 文档学习完成！")
        print("=" * 70)
        print(f"\n下一步: 运行增量索引更新")
        print(f"  python3 incremental_index.py {output_path}")

        return True
    else:
        print("\n" + "=" * 70)
        print("❌ 获取文档失败")
        print("=" * 70)
        print(f"\n错误: {result['error']}")
        print("\n故障排查:")
        print("  1. 检查文档URL/ID是否正确")
        print("  2. 检查飞书应用是否有访问该文档的权限")
        print("  3. 检查 .env 中的 FEISHU_APP_ID 和 FEISHU_APP_SECRET")

        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
