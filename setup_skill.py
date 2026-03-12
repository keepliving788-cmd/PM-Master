#!/usr/bin/env python3
"""
OpenClaw Skill初始化脚本
"""
import os
import sys
from pathlib import Path


def setup():
    """初始化Skill"""
    print("=" * 70)
    print("飞书离线知识库 Skill - 初始化")
    print("=" * 70)

    skill_dir = Path(__file__).parent

    # 1. 检查.env文件
    print("\n[1] 检查配置文件...")
    env_file = skill_dir / '.env'
    env_example = skill_dir / '.env.example'

    if not env_file.exists():
        if env_example.exists():
            print("  ⚠️  未找到 .env 文件")
            print("  请复制 .env.example 并填写配置:")
            print(f"     cp .env.example .env")
            print(f"     然后编辑 .env 填写飞书凭证")
            return False
        else:
            print("  ❌ 未找到配置文件")
            return False
    else:
        print("  ✅ 配置文件存在")

    # 2. 检查依赖
    print("\n[2] 检查Python依赖...")
    required_packages = [
        'flask',
        'numpy',
        'sklearn',
        'rank_bm25',
        'jieba',
        'lark_oapi',
        'loguru',
        'yaml'
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (缺失)")
            missing.append(package)

    if missing:
        print(f"\n  请安装缺失的依赖:")
        print(f"     pip install -r requirements.txt")
        return False

    # 3. 检查是否需要构建索引
    print("\n[3] 检查知识库索引...")
    data_dir = skill_dir / 'data'

    required_files = [
        data_dir / 'vectors.npz',
        data_dir / 'bm25_index.pkl',
        data_dir / 'kb_data.db'
    ]

    all_exist = all(f.exists() for f in required_files)

    if all_exist:
        print("  ✅ 知识库索引已存在")

        # 显示索引信息
        import json
        metadata_file = data_dir / 'metadata.json'
        if metadata_file.exists():
            with open(metadata_file) as f:
                metadata = json.load(f)
            print(f"     构建时间: {metadata['build_time']}")
            print(f"     文档块数: {metadata['chunk_count']}")
            print(f"     向量维度: {metadata['vector_dimension']}")
    else:
        print("  ⚠️  知识库索引未构建")
        print("     需要运行: /feishu-kb update")
        print("     或手动运行:")
        print("       python3 fetch_wiki_content.py")
        print("       python3 build_offline_kb_fast.py")

    print("\n" + "=" * 70)
    print("✅ Skill初始化完成")
    print("=" * 70)

    print("\n使用方法:")
    print("  /feishu-kb search <查询>    - 搜索知识库")
    print("  /feishu-kb update          - 更新知识库")
    print("  /feishu-kb status          - 查看状态")

    print("\n示例:")
    print("  /feishu-kb search 扫码王")
    print("  /feishu-kb search 收钱吧APP功能")

    if not all_exist:
        print("\n⚠️  记得先运行 /feishu-kb update 构建知识库索引")

    return True


if __name__ == '__main__':
    success = setup()
    sys.exit(0 if success else 1)
