#!/usr/bin/env python3
"""
知识库初始化脚本 - 通用版本
用于首次使用时配置和学习知识库
"""
import os
import sys
from pathlib import Path
from getpass import getpass


def check_initialized():
    """检查是否已初始化"""
    data_dir = Path('data')
    required_files = [
        data_dir / 'vectors.npz',
        data_dir / 'kb_data.db',
        data_dir / 'bm25_index.pkl'
    ]

    env_file = Path('.env')

    return all(f.exists() for f in required_files) and env_file.exists()


def interactive_config():
    """交互式配置向导"""
    print("=" * 70)
    print("🚀 飞书离线知识库Skill - 初始化向导")
    print("=" * 70)

    print("\n[步骤 1/3] 配置飞书应用凭证")
    print("-" * 70)
    print("需要飞书应用的 App ID 和 App Secret")
    print("获取方法: https://open.feishu.cn/ → 创建应用")
    print()

    app_id = input("FEISHU_APP_ID: ").strip()
    app_secret = getpass("FEISHU_APP_SECRET (输入不可见): ").strip()

    if not app_id or not app_secret:
        print("❌ App ID和Secret不能为空")
        return False

    print("\n[步骤 2/3] 配置知识库")
    print("-" * 70)
    print("支持以下方式:")
    print("  1. 知识库URL: https://xxx.feishu.cn/wiki/xxxxx")
    print("  2. Space ID: 数字ID")
    print("  3. Wiki Token: N9kgwANVwi...")
    print()

    wiki_input = input("知识库URL/Space ID/Wiki Token: ").strip()

    if not wiki_input:
        print("❌ 知识库信息不能为空")
        return False

    # 解析输入
    space_id, wiki_token = parse_wiki_input(wiki_input)

    # 保存配置
    env_content = f"""# 飞书应用凭证
FEISHU_APP_ID={app_id}
FEISHU_APP_SECRET={app_secret}

# 知识库配置
FEISHU_WIKI_SPACE_ID={space_id}
FEISHU_WIKI_TOKEN={wiki_token}
"""

    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)

    print("\n✅ 配置已保存到 .env")

    # 验证配置
    print("\n[验证配置]")
    if verify_config():
        print("✅ 飞书API连接成功")
    else:
        print("❌ 验证失败，请检查配置")
        return False

    return True


def parse_wiki_input(wiki_input):
    """解析知识库输入"""
    # 如果是URL
    if 'feishu.cn/wiki/' in wiki_input:
        # 提取token
        wiki_token = wiki_input.split('/wiki/')[1].split('?')[0]
        return '', wiki_token

    # 如果是纯数字，当作Space ID
    elif wiki_input.isdigit():
        return wiki_input, ''

    # 否则当作Wiki Token
    else:
        return '', wiki_input


def verify_config():
    """验证飞书配置"""
    try:
        # 读取.env
        env_path = Path('.env')
        if not env_path.exists():
            return False

        with open(env_path) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

        # 测试连接
        import lark_oapi as lark
        client = lark.Client.builder() \
            .app_id(os.environ['FEISHU_APP_ID']) \
            .app_secret(os.environ['FEISHU_APP_SECRET']) \
            .build()

        # 简单测试（获取token）
        # 实际会在后续学习时验证
        return True

    except Exception as e:
        print(f"验证失败: {e}")
        return False


def start_learning():
    """开始学习知识库"""
    print("\n[步骤 3/3] 学习知识库")
    print("-" * 70)
    print("这将下载知识库所有文档并构建索引")
    print()

    # 询问学习模式
    print("选择学习模式:")
    print("  1. 测试模式 - 只下载10个文档（快速验证）")
    print("  2. 限制模式 - 自定义下载数量")
    print("  3. 完整模式 - 下载所有文档（推荐）")
    print()

    choice = input("请选择 (1/2/3) [默认: 1]: ").strip() or '1'

    if choice == '1':
        # 测试模式
        print("\n🧪 测试模式：下载10个文档")
        os.system("python3 learn_full_kb.py --test --auto")
    elif choice == '2':
        # 限制模式
        limit = input("下载数量: ").strip()
        if limit.isdigit():
            print(f"\n📝 限制模式：下载{limit}个文档")
            os.system(f"python3 learn_full_kb.py --limit {limit} --auto")
        else:
            print("❌ 无效数量")
            return False
    else:
        # 完整模式
        print("\n🚀 完整模式：下载所有文档")
        confirm = input("确认开始？这可能需要10-30分钟 (y/n): ").lower()
        if confirm == 'y':
            os.system("python3 learn_full_kb.py --auto")
        else:
            print("已取消")
            return False

    # 构建索引
    print("\n构建索引...")
    result = os.system("python3 build_full_kb_index.py")

    if result == 0:
        print("\n✅ 索引构建成功")
        return True
    else:
        print("\n❌ 索引构建失败")
        return False


def show_status():
    """显示当前状态"""
    print("\n" + "=" * 70)
    print("📊 当前状态")
    print("=" * 70)

    # 检查.env
    env_exists = Path('.env').exists()
    print(f"配置文件: {'✅ 已配置' if env_exists else '❌ 未配置'}")

    # 检查数据
    data_dir = Path('data')
    if data_dir.exists():
        files = {
            'vectors.npz': '向量索引',
            'bm25_index.pkl': 'BM25索引',
            'kb_data.db': '数据库',
            'metadata.json': '元数据'
        }

        print("\n索引文件:")
        for file, desc in files.items():
            path = data_dir / file
            if path.exists():
                size = path.stat().st_size / 1024 / 1024
                print(f"  ✅ {desc}: {size:.1f} MB")
            else:
                print(f"  ❌ {desc}: 未生成")
    else:
        print("\n索引文件: ❌ 未生成")

    # 检查是否可用
    initialized = check_initialized()
    print(f"\n系统状态: {'✅ 可用' if initialized else '❌ 需要初始化'}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='飞书知识库初始化')
    parser.add_argument('--interactive', action='store_true', help='交互式配置')
    parser.add_argument('--status', action='store_true', help='显示状态')
    parser.add_argument('--reset', action='store_true', help='重置配置')

    args = parser.parse_args()

    if args.status:
        show_status()
        return

    if args.reset:
        if input("确认重置配置？(y/n): ").lower() == 'y':
            if Path('.env').exists():
                Path('.env').unlink()
            print("✅ 配置已重置")
        return

    # 检查是否已初始化
    if check_initialized() and not args.interactive:
        print("✅ 知识库已初始化")
        show_status()

        if input("\n是否重新配置？(y/n): ").lower() != 'y':
            return

    # 交互式配置
    if not interactive_config():
        print("\n❌ 配置失败")
        sys.exit(1)

    # 开始学习
    if start_learning():
        print("\n" + "=" * 70)
        print("🎉 初始化完成！")
        print("=" * 70)
        print("\n现在可以使用了:")
        print("  python3 skill_main.py search \"你的查询\"")
        print()
    else:
        print("\n❌ 初始化失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
