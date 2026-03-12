#!/usr/bin/env python3
"""
自动查找飞书知识空间Space ID
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

    print("=" * 60)
    print("🔍 飞书知识空间 Space ID 查找工具")
    print("=" * 60)
    print()

    if not app_id or not app_secret:
        print("❌ 错误: 未找到 FEISHU_APP_ID 或 FEISHU_APP_SECRET")
        print("   请先配置 .env 文件")
        return

    print(f"✅ App ID: {app_id[:15]}...")
    print(f"✅ App Secret: {'*' * 20}")
    print()

    # 创建客户端
    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(app_secret) \
        .build()

    print("📚 正在获取知识空间列表...")
    print()

    try:
        # 获取知识空间列表
        request = ListSpaceRequest.builder().build()
        response = client.wiki.v2.space.list(request)

        if not response.success():
            print(f"❌ API调用失败")
            print(f"   错误码: {response.code}")
            print(f"   错误信息: {response.msg}")
            print()
            print("💡 可能的原因:")
            print("   1. 应用权限不足 - 需要 wiki:wiki:readonly 权限")
            print("   2. 应用未发布")
            print("   3. 账号无知识空间访问权限")
            return

        # 显示结果
        spaces = response.data.items

        if not spaces:
            print("⚠️  未找到任何知识空间")
            print()
            print("💡 可能原因:")
            print("   1. 你的账号没有任何知识空间访问权限")
            print("   2. 应用权限未正确配置")
            return

        print(f"✅ 找到 {len(spaces)} 个知识空间:")
        print()
        print("-" * 60)

        for i, space in enumerate(spaces, 1):
            print(f"\n[{i}] 知识空间名称: {space.name}")
            print(f"    Space ID: {space.space_id}")
            print(f"    类型: {space.space_type}")
            print(f"    描述: {space.description or '(无)'}")

        print()
        print("-" * 60)
        print()
        print("📝 使用方法:")
        print()
        print("1. 从上面选择你需要的知识空间的 Space ID")
        print("2. 编辑 .env 文件:")
        print("   nano .env")
        print()
        print("3. 修改为:")
        print("   FEISHU_WIKI_SPACE_ID=<你的Space ID>")
        print()
        print("4. 保存后测试:")
        print("   python3 test_api_access.py")
        print()

    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
