#!/usr/bin/env python3
"""
测试不同的飞书API，找出哪个可以用
"""
import os
from dotenv import load_dotenv
import lark_oapi as lark
from lark_oapi.api.wiki.v2 import *

load_dotenv()

def test_apis():
    """测试多个API"""

    app_id = os.getenv('FEISHU_APP_ID')
    app_secret = os.getenv('FEISHU_APP_SECRET')
    space_id = os.getenv('FEISHU_WIKI_SPACE_ID')
    wiki_token = 'N9kgwANVwifcisk9UT6cDOFInRe'

    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(app_secret) \
        .build()

    print("=" * 70)
    print("测试不同的飞书API")
    print("=" * 70)

    # 测试1: 列出所有知识空间
    print("\n[测试1] 列出所有知识空间")
    try:
        request = ListSpaceRequest.builder().build()
        response = client.wiki.v2.space.list(request)

        if response.success():
            print(f"✅ 成功！找到 {len(response.data.items) if response.data.items else 0} 个空间")
            if response.data.items:
                for space in response.data.items:
                    print(f"   - {space.name} (ID: {space.space_id})")
        else:
            print(f"❌ 失败: [{response.code}] {response.msg}")
    except Exception as e:
        print(f"❌ 异常: {e}")

    # 测试2: 获取指定空间信息
    print("\n[测试2] 获取指定空间信息")
    try:
        request = GetSpaceRequest.builder() \
            .space_id(space_id) \
            .build()
        response = client.wiki.v2.space.get(request)

        if response.success():
            print(f"✅ 成功！空间名称: {response.data.space.name}")
        else:
            print(f"❌ 失败: [{response.code}] {response.msg}")
    except Exception as e:
        print(f"❌ 异常: {e}")

    # 测试3: 通过Wiki Token获取节点信息
    print("\n[测试3] 通过Wiki Token获取节点信息")
    try:
        request = GetNodeSpaceRequest.builder() \
            .token(wiki_token) \
            .build()
        response = client.wiki.v2.space.get_node(request)

        if response.success():
            print(f"✅ 成功！节点类型: {response.data.node.obj_type}")
            print(f"   Space ID: {response.data.node.space_id}")
            print(f"   Obj Token: {response.data.node.obj_token}")
        else:
            print(f"❌ 失败: [{response.code}] {response.msg}")
    except Exception as e:
        print(f"❌ 异常: {e}")

    # 测试4: 列出空间节点
    print("\n[测试4] 列出空间节点")
    try:
        request = ListSpaceNodeRequest.builder() \
            .space_id(space_id) \
            .page_size(10) \
            .build()
        response = client.wiki.v2.space_node.list(request)

        if response.success():
            print(f"✅ 成功！获取 {len(response.data.items) if response.data.items else 0} 个节点")
        else:
            print(f"❌ 失败: [{response.code}] {response.msg}")
    except Exception as e:
        print(f"❌ 异常: {e}")

    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)

if __name__ == '__main__':
    test_apis()
