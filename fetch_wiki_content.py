#!/usr/bin/env python3
"""
直接从飞书获取知识库内容
"""
import os
import sys
from pathlib import Path

# 直接读取.env
env_path = Path(__file__).parent / '.env'
with open(env_path) as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

import lark_oapi as lark
from lark_oapi.api.wiki.v2 import *
from lark_oapi.api.docx.v1 import *

def main():
    print("=" * 70)
    print("从飞书获取知识库内容")
    print("=" * 70)

    app_id = os.environ['FEISHU_APP_ID']
    app_secret = os.environ['FEISHU_APP_SECRET']
    wiki_token = 'N9kgwANVwifcisk9UT6cDOFInRe'

    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(app_secret) \
        .build()

    print(f"\n✅ APP_ID: {app_id[:15]}...")

    # 方法1: 通过Wiki Token获取节点
    print("\n[步骤1] 获取Wiki节点信息...")
    try:
        request = GetNodeSpaceRequest.builder().token(wiki_token).build()
        response = client.wiki.v2.space.get_node(request)

        if not response.success():
            print(f"❌ 失败: [{response.code}] {response.msg}")

            # 尝试备用方法：直接通过space_id获取
            print("\n[备用方法] 尝试通过Space ID获取...")
            space_id = os.environ.get('FEISHU_WIKI_SPACE_ID')

            request = ListSpaceNodeRequest.builder() \
                .space_id(space_id) \
                .page_size(100) \
                .build()
            response = client.wiki.v2.space_node.list(request)

            if not response.success():
                print(f"❌ 备用方法也失败: [{response.code}] {response.msg}")
                print("\n尝试最后一种方法：使用文档API...")

                # 尝试直接作为文档ID获取
                return try_as_document(client, wiki_token)
            else:
                print(f"✅ 获取到 {len(response.data.items)} 个节点")
                # 遍历所有节点获取内容
                all_content = []
                for item in response.data.items:
                    content = get_node_content(client, item)
                    if content:
                        all_content.append(content)

                save_content(all_content)
                return True
        else:
            node = response.data.node
            print(f"✅ 节点信息:")
            print(f"   类型: {node.obj_type}")
            print(f"   Space ID: {node.space_id}")
            print(f"   Obj Token: {node.obj_token}")

            # 获取内容
            content = get_node_content(client, node)
            if content:
                save_content([content])
                return True

    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()

    return False

def get_node_content(client, node):
    """获取节点内容"""
    try:
        if node.obj_type in ['docx', 'doc']:
            print(f"\n[获取] 文档内容: {node.obj_token}")

            request = RawContentDocumentRequest.builder() \
                .document_id(node.obj_token) \
                .lang(0) \
                .build()

            response = client.docx.v1.document.raw_content(request)

            if response.success():
                print(f"   ✅ 成功 ({len(response.data.content)} 字符)")
                return response.data.content
            else:
                print(f"   ❌ 失败: {response.msg}")

    except Exception as e:
        print(f"   ❌ 异常: {e}")

    return None

def try_as_document(client, doc_id):
    """尝试作为文档ID直接获取"""
    print(f"\n[尝试] 作为文档ID获取: {doc_id}")

    try:
        request = RawContentDocumentRequest.builder() \
            .document_id(doc_id) \
            .lang(0) \
            .build()

        response = client.docx.v1.document.raw_content(request)

        if response.success():
            print(f"✅ 成功获取文档内容！")
            print(f"   长度: {len(response.data.content)} 字符")
            save_content([response.data.content])
            return True
        else:
            print(f"❌ 失败: [{response.code}] {response.msg}")

    except Exception as e:
        print(f"❌ 异常: {e}")

    return False

def save_content(contents):
    """保存内容"""
    # 创建目录
    Path('data/raw').mkdir(parents=True, exist_ok=True)

    # 合并所有内容
    full_content = '\n\n---\n\n'.join(contents)

    # 保存
    output_path = 'data/raw/wiki_content.txt'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_content)

    print(f"\n{'='*70}")
    print(f"✅ 成功保存内容！")
    print(f"{'='*70}")
    print(f"文件: {output_path}")
    print(f"大小: {len(full_content)} 字符")
    print(f"预览:\n{full_content[:500]}...")

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
