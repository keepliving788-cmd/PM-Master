#!/usr/bin/env python3
"""
下载海外业务文档及其嵌入子文档
URL: https://sqb.feishu.cn/wiki/FyEfwXZLNibL9yk7IkmchNFVnoh
"""
import os
import sys
import json
import time
from pathlib import Path

# 读取.env
env_path = Path(__file__).parent / '.env'
with open(env_path) as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

import lark_oapi as lark
from lark_oapi.api.wiki.v2 import *
from lark_oapi.api.docx.v1 import *


class OverseasDocFetcher:
    """海外业务文档获取器"""

    def __init__(self):
        self.client = lark.Client.builder() \
            .app_id(os.environ['FEISHU_APP_ID']) \
            .app_secret(os.environ['FEISHU_APP_SECRET']) \
            .build()

        # 海外业务文档的wiki token
        self.overseas_wiki_token = 'FyEfwXZLNibL9yk7IkmchNFVnoh'

        self.data_dir = Path('data/raw')
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def fetch_document(self, doc_id: str, title: str = "文档") -> dict:
        """获取单个文档内容"""
        print(f"📄 获取文档: {title}")
        print(f"   Token: {doc_id}")

        try:
            request = RawContentDocumentRequest.builder() \
                .document_id(doc_id) \
                .lang(0) \
                .build()

            response = self.client.docx.v1.document.raw_content(request)

            if response.success():
                content = response.data.content
                print(f"   ✅ 成功 ({len(content):,} 字符)")

                return {
                    'title': title,
                    'doc_id': doc_id,
                    'content': content,
                    'length': len(content)
                }
            else:
                print(f"   ❌ 失败: {response.msg}")
                return None

        except Exception as e:
            print(f"   ❌ 异常: {e}")
            return None

    def get_wiki_node_info(self) -> dict:
        """获取Wiki节点信息"""
        print(f"🔍 获取Wiki节点信息...")
        print(f"   Wiki Token: {self.overseas_wiki_token}")

        try:
            request = GetNodeSpaceRequest.builder() \
                .token(self.overseas_wiki_token) \
                .build()

            response = self.client.wiki.v2.space.get_node(request)

            if response.success():
                node = response.data.node
                print(f"   ✅ 成功")
                print(f"   标题: {node.title if hasattr(node, 'title') else '(无标题)'}")
                print(f"   类型: {node.obj_type}")
                print(f"   Space ID: {node.space_id}")
                print(f"   Obj Token: {node.obj_token}")

                return {
                    'title': node.title if hasattr(node, 'title') else '海外业务文档',
                    'obj_token': node.obj_token,
                    'obj_type': node.obj_type,
                    'space_id': node.space_id
                }
            else:
                print(f"   ⚠️ 获取节点信息失败: {response.msg}")
                print(f"   尝试直接作为文档获取...")
                return {
                    'title': '海外业务文档',
                    'obj_token': self.overseas_wiki_token,
                    'obj_type': 'docx',
                    'space_id': None
                }

        except Exception as e:
            print(f"   ⚠️ 异常: {e}")
            return {
                'title': '海外业务文档',
                'obj_token': self.overseas_wiki_token,
                'obj_type': 'docx',
                'space_id': None
            }

    def extract_embedded_docs(self, content: str) -> list:
        """从文档内容中提取嵌入的文档链接"""
        import re

        # 匹配飞书文档链接模式
        patterns = [
            r'https://sqb\.feishu\.cn/(?:wiki|docx|docs)/([a-zA-Z0-9]+)',
            r'feishu://docx/([a-zA-Z0-9]+)',
        ]

        embedded_docs = set()

        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                doc_id = match.group(1)
                embedded_docs.add(doc_id)

        return list(embedded_docs)

    def fetch_all(self):
        """获取主文档及所有嵌入的子文档"""
        print("=" * 70)
        print("🌏 下载海外业务文档")
        print("=" * 70)
        print()

        # 步骤1: 获取主文档信息
        node_info = self.get_wiki_node_info()
        print()

        # 步骤2: 下载主文档
        print("[步骤 1/3] 下载主文档")
        print("-" * 70)
        main_doc = self.fetch_document(
            node_info['obj_token'],
            node_info['title']
        )

        if not main_doc:
            print("❌ 主文档下载失败")
            return False

        all_docs = [main_doc]
        print()

        # 步骤3: 提取并下载嵌入文档
        print("[步骤 2/3] 查找嵌入文档")
        print("-" * 70)
        embedded_doc_ids = self.extract_embedded_docs(main_doc['content'])

        if embedded_doc_ids:
            print(f"✅ 发现 {len(embedded_doc_ids)} 个嵌入文档")
            print()

            for i, doc_id in enumerate(embedded_doc_ids, 1):
                print(f"[{i}/{len(embedded_doc_ids)}] ", end='')
                doc = self.fetch_document(doc_id, f"嵌入文档-{i}")

                if doc:
                    all_docs.append(doc)

                # 避免请求过快
                time.sleep(0.2)
        else:
            print("ℹ️  未发现嵌入文档")

        print()

        # 步骤4: 保存内容
        print("[步骤 3/3] 保存文档内容")
        print("-" * 70)
        self.save_documents(all_docs)

        print()
        print("=" * 70)
        print("✅ 海外业务文档下载完成！")
        print("=" * 70)
        print()
        print(f"📊 统计:")
        print(f"   主文档: 1 个")
        print(f"   嵌入文档: {len(all_docs) - 1} 个")
        print(f"   总文档: {len(all_docs)} 个")
        print(f"   总字符: {sum(doc['length'] for doc in all_docs):,}")
        print()

        return True

    def save_documents(self, docs: list):
        """保存文档内容"""
        # 保存到单独的文件
        output_file = self.data_dir / 'overseas_content.txt'

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("收钱吧海外业务文档\n")
            f.write("=" * 70 + "\n\n")

            for doc in docs:
                f.write("=" * 70 + "\n")
                f.write(f"文档: {doc['title']}\n")
                f.write(f"ID: {doc['doc_id']}\n")
                f.write("=" * 70 + "\n\n")
                f.write(doc['content'])
                f.write("\n\n")

        total_chars = sum(doc['length'] for doc in docs)

        print(f"✅ 保存到: {output_file}")
        print(f"   文档数: {len(docs)}")
        print(f"   总字符: {total_chars:,}")
        print(f"   文件大小: {total_chars / 1024:.2f} KB")

        # 保存元数据
        metadata = {
            'source': 'overseas_business',
            'wiki_token': self.overseas_wiki_token,
            'total_docs': len(docs),
            'total_chars': total_chars,
            'fetch_time': time.strftime("%Y-%m-%d %H:%M:%S"),
            'documents': [
                {
                    'title': doc['title'],
                    'doc_id': doc['doc_id'],
                    'length': doc['length']
                }
                for doc in docs
            ]
        }

        metadata_file = self.data_dir / 'overseas_metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"✅ 元数据: {metadata_file}")


def main():
    fetcher = OverseasDocFetcher()
    success = fetcher.fetch_all()

    if success:
        print("📝 下一步:")
        print("   1. 合并到完整知识库:")
        print("      python3 merge_overseas_to_kb.py")
        print()
        print("   2. 或者直接重建索引:")
        print("      python3 build_full_kb_index.py")

    return success


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  已取消")
        sys.exit(1)
