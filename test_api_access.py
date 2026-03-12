#!/usr/bin/env python3
"""
测试飞书 API 访问
用于验证应用凭证和权限是否配置正确
"""
import os
from dotenv import load_dotenv
import lark_oapi as lark
from lark_oapi.api.wiki.v2 import *

# 加载环境变量
load_dotenv()

def test_api_access():
    """测试 API 访问"""

    print("=" * 60)
    print("飞书 API 访问测试")
    print("=" * 60)

    # 1. 检查环境变量
    print("\n[1] 检查环境变量...")
    app_id = os.getenv('FEISHU_APP_ID')
    app_secret = os.getenv('FEISHU_APP_SECRET')
    space_id = os.getenv('FEISHU_WIKI_SPACE_ID')

    if not app_id or not app_secret:
        print("❌ 错误：未配置 FEISHU_APP_ID 或 FEISHU_APP_SECRET")
        print("请编辑 .env 文件添加配置")
        return False

    print(f"✅ App ID: {app_id[:10]}...")
    print(f"✅ App Secret: {'*' * 20}")
    print(f"✅ Space ID: {space_id}")

    # 2. 创建客户端
    print("\n[2] 创建飞书客户端...")
    try:
        client = lark.Client.builder() \
            .app_id(app_id) \
            .app_secret(app_secret) \
            .build()
        print("✅ 客户端创建成功")
    except Exception as e:
        print(f"❌ 客户端创建失败: {e}")
        return False

    # 3. 测试获取知识空间节点
    print("\n[3] 测试获取知识空间节点...")
    try:
        request = ListSpaceNodeRequest.builder() \
            .space_id(space_id) \
            .page_size(10) \
            .build()

        response = client.wiki.v2.space_node.list(request)

        if not response.success():
            print(f"❌ API 调用失败")
            print(f"   错误码: {response.code}")
            print(f"   错误信息: {response.msg}")

            # 常见错误提示
            if response.code == 99991663:
                print("\n💡 可能的原因：")
                print("   1. 应用未开启 wiki:wiki:readonly 权限")
                print("   2. 应用未发布或未添加到企业")
                print("   3. Space ID 不正确")
            elif response.code == 99991401:
                print("\n💡 可能的原因：")
                print("   1. App ID 或 App Secret 不正确")
                print("   2. 应用被禁用")

            return False

        # 成功获取节点
        node_count = len(response.data.items) if response.data.items else 0
        print(f"✅ 成功获取 {node_count} 个节点")

        if node_count > 0:
            print("\n节点列表：")
            for i, node in enumerate(response.data.items[:5], 1):
                print(f"   {i}. {node.node_type} - Token: {node.node_token}")

        return True

    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)

if __name__ == '__main__':
    success = test_api_access()

    if success:
        print("\n🎉 测试通过！可以开始构建索引了")
        print("\n下一步：")
        print("  python src/main.py index --full")
    else:
        print("\n❌ 测试失败，请检查配置")
        print("\n排查步骤：")
        print("  1. 确认 .env 文件配置正确")
        print("  2. 确认应用已发布到企业")
        print("  3. 确认应用有 wiki:wiki:readonly 权限")
        print("  4. 确认 Space ID 正确")
        print("\n详细文档：https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/wiki-overview")
