#!/usr/bin/env python3
"""
从Wiki URL获取Space ID
URL: https://sqb.feishu.cn/wiki/N9kgwANVwifcisk9UT6cDOFInRe?fromScene=spaceOverview
"""
import os
from dotenv import load_dotenv
import lark_oapi as lark
from lark_oapi.api.wiki.v2 import *

def main():
    # 加载环境变量
    load_dotenv()

    app_id = os.getenv('FEISHU_APP_ID')
    app_secret = os.getenv('FEISHU_APP_SECRET')

    # 从URL提取的wiki token
    wiki_token = "N9kgwANVwifcisk9UT6cDOFInRe"

    print("=" * 70)
    print("🔍 从Wiki Token获取Space ID")
    print("=" * 70)
    print()
    print(f"📌 Wiki URL: https://sqb.feishu.cn/wiki/{wiki_token}")
    print(f"📌 Wiki Token: {wiki_token}")
    print()

    if not app_id or not app_secret:
        print("❌ 错误: 未找到飞书凭证")
        return

    print(f"✅ App ID: {app_id[:15]}...")
    print(f"✅ App Secret: {'*' * 20}")
    print()

    # 创建客户端
    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(app_secret) \
        .build()

    print("🔄 正在获取Wiki节点信息...")
    print()

    try:
        # 方法1: 使用 get_node API
        request = GetNodeSpaceRequest.builder() \
            .token(wiki_token) \
            .build()

        response = client.wiki.v2.space.get_node(request)

        if response.success():
            node = response.data.node
            space_id = node.space_id

            print("✅ 成功获取Space ID!")
            print()
            print("=" * 70)
            print(f"📊 知识空间信息:")
            print("-" * 70)
            print(f"  空间名称: {node.title if hasattr(node, 'title') else '(未知)'}")
            print(f"  Space ID: {space_id}")
            print(f"  节点类型: {node.obj_type if hasattr(node, 'obj_type') else '(未知)'}")
            print(f"  Wiki Token: {wiki_token}")
            print("=" * 70)
            print()

            # 提供配置指导
            print("📝 下一步操作:")
            print()
            print("1. 编辑 .env 文件:")
            print("   nano .env")
            print()
            print("2. 修改 FEISHU_WIKI_SPACE_ID 为:")
            print(f"   FEISHU_WIKI_SPACE_ID={space_id}")
            print()
            print("3. 保存后测试:")
            print("   python3 test_api_access.py")
            print()
            print("4. 如果测试通过，构建索引:")
            print("   python3 src/main.py index --full")
            print()

            # 自动更新.env文件
            print("💡 是否自动更新 .env 文件? (y/n): ", end='', flush=True)
            choice = input().strip().lower()

            if choice == 'y':
                update_env_file(space_id)
            else:
                print("   请手动更新 .env 文件")

        else:
            print(f"❌ 获取失败")
            print(f"   错误码: {response.code}")
            print(f"   错误信息: {response.msg}")
            print()

            # 尝试方法2
            print("🔄 尝试其他方法...")
            try_alternative_method(client, wiki_token)

    except Exception as e:
        print(f"❌ 发生错误: {e}")
        print()
        print("尝试使用备选方法...")
        try_alternative_method(client, wiki_token)

def try_alternative_method(client, wiki_token):
    """尝试通过列出所有space来匹配"""
    print()
    print("📚 方法2: 列出所有知识空间...")
    print()

    try:
        request = ListSpaceRequest.builder().build()
        response = client.wiki.v2.space.list(request)

        if response.success() and response.data.items:
            print(f"✅ 找到 {len(response.data.items)} 个知识空间:")
            print()

            for i, space in enumerate(response.data.items, 1):
                print(f"[{i}] {space.name}")
                print(f"    Space ID: {space.space_id}")
                print()

            print("💡 请从上面选择对应的Space ID，手动配置到 .env 文件")
        else:
            print("❌ 未找到任何知识空间")
            print()
            print("可能原因:")
            print("  1. 应用权限不足")
            print("  2. 应用未发布")
            print("  3. 账号没有知识空间访问权限")

    except Exception as e:
        print(f"❌ 备选方法也失败了: {e}")

def update_env_file(space_id):
    """自动更新.env文件"""
    try:
        # 读取现有内容
        with open('.env', 'r') as f:
            lines = f.readlines()

        # 更新FEISHU_WIKI_SPACE_ID
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('FEISHU_WIKI_SPACE_ID='):
                lines[i] = f'FEISHU_WIKI_SPACE_ID={space_id}\n'
                updated = True
                break

        # 如果没找到这一行，追加
        if not updated:
            lines.append(f'\nFEISHU_WIKI_SPACE_ID={space_id}\n')

        # 写回文件
        with open('.env', 'w') as f:
            f.writelines(lines)

        print()
        print("✅ .env 文件已自动更新!")
        print()
        print("下一步:")
        print("  python3 test_api_access.py")

    except Exception as e:
        print(f"❌ 更新失败: {e}")
        print("   请手动更新 .env 文件")

if __name__ == "__main__":
    main()
