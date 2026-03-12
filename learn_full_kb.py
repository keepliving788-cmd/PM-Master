#!/usr/bin/env python3
"""
完整知识库学习脚本 - 一次性获取所有1597个文档
"""
import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict

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


class FullKBLearner:
    """完整知识库学习器"""

    def __init__(self):
        self.client = lark.Client.builder() \
            .app_id(os.environ['FEISHU_APP_ID']) \
            .app_secret(os.environ['FEISHU_APP_SECRET']) \
            .build()

        self.space_id = os.environ['FEISHU_WIKI_SPACE_ID']
        self.root_token = os.environ.get('FEISHU_WIKI_TOKEN', 'N9kgwANVwifcisk9UT6cDOFInRe')

        self.data_dir = Path('data/raw')
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.cache_file = self.data_dir / 'nodes_cache.json'
        self.progress_file = self.data_dir / 'download_progress.json'

    def get_all_nodes(self, use_cache=True) -> List:
        """获取所有文档节点"""

        # 尝试从缓存加载
        if use_cache and self.cache_file.exists():
            print("📦 从缓存加载节点列表...")
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                nodes_data = json.load(f)
            print(f"✅ 加载了 {len(nodes_data)} 个节点")
            return nodes_data

        print("🔍 递归获取知识库所有节点...")
        nodes = self._get_nodes_recursive(self.space_id, self.root_token)

        # 过滤出文档类型
        doc_nodes = [n for n in nodes if n['obj_type'] == 'docx']

        print(f"✅ 发现 {len(doc_nodes)} 个文档节点")

        # 保存缓存
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(doc_nodes, f, ensure_ascii=False, indent=2)

        return doc_nodes

    def _get_nodes_recursive(self, space_id, parent_token=None, level=0) -> List:
        """递归获取节点"""
        nodes = []

        request = ListSpaceNodeRequest.builder() \
            .space_id(space_id) \
            .page_size(50)

        if parent_token:
            request = request.parent_node_token(parent_token)

        request = request.build()

        try:
            response = self.client.wiki.v2.space_node.list(request)

            if not response.success():
                if level == 0:
                    print(f"  ⚠️ 根节点获取失败: {response.msg}")
                return nodes

            items = response.data.items if response.data.items else []

            for item in items:
                node_data = {
                    'title': item.title,
                    'node_token': item.node_token,
                    'obj_token': item.obj_token,
                    'obj_type': item.obj_type,
                    'has_child': item.has_child,
                    'level': level
                }
                nodes.append(node_data)

                # 递归获取子节点
                if item.has_child:
                    children = self._get_nodes_recursive(space_id, item.node_token, level + 1)
                    nodes.extend(children)

            # 处理分页
            if response.data.has_more:
                print(f"  {'  '*level}⚠️ 还有更多节点（分页未实现）")

        except Exception as e:
            print(f"  ⚠️ 获取节点失败: {e}")

        return nodes

    def download_all_documents(self, nodes: List[Dict], max_docs=None) -> List[Dict]:
        """批量下载所有文档内容"""

        # 加载进度
        progress = self._load_progress()
        downloaded = progress.get('downloaded', {})

        docs_to_download = nodes[:max_docs] if max_docs else nodes
        total = len(docs_to_download)

        print(f"\n📥 开始下载文档内容...")
        print(f"总计: {total} 个文档")
        print(f"已完成: {len(downloaded)} 个")
        print(f"剩余: {total - len(downloaded)} 个")
        print("=" * 70)

        all_contents = []
        success_count = 0
        fail_count = 0
        skip_count = len(downloaded)

        for i, node in enumerate(docs_to_download, 1):
            obj_token = node['obj_token']
            title = node['title']

            # 检查是否已下载
            if obj_token in downloaded:
                all_contents.append(downloaded[obj_token])
                continue

            # 显示进度
            print(f"[{i}/{total}] {title[:50]:<50s}", end=' ... ', flush=True)

            try:
                # 下载文档
                content = self._fetch_document(obj_token)

                if content:
                    doc_data = {
                        'title': title,
                        'obj_token': obj_token,
                        'node_token': node['node_token'],
                        'content': content,
                        'length': len(content)
                    }
                    all_contents.append(doc_data)
                    downloaded[obj_token] = doc_data

                    print(f"✅ {len(content)} 字符")
                    success_count += 1

                    # 每10个文档保存一次进度
                    if success_count % 10 == 0:
                        self._save_progress({
                            'downloaded': downloaded,
                            'success': success_count + skip_count,
                            'failed': fail_count,
                            'total': total
                        })

                else:
                    print("⚠️ 空内容")
                    fail_count += 1

                # 避免请求过快
                time.sleep(0.1)

            except Exception as e:
                print(f"❌ 失败: {e}")
                fail_count += 1

        # 保存最终进度
        self._save_progress({
            'downloaded': downloaded,
            'success': success_count + skip_count,
            'failed': fail_count,
            'total': total,
            'completed': True
        })

        print("=" * 70)
        print(f"下载完成:")
        print(f"  成功: {success_count} 个")
        print(f"  跳过: {skip_count} 个（已下载）")
        print(f"  失败: {fail_count} 个")
        print(f"  总计: {success_count + skip_count} 个")

        return all_contents

    def _fetch_document(self, obj_token: str) -> str:
        """获取单个文档内容"""
        request = RawContentDocumentRequest.builder() \
            .document_id(obj_token) \
            .lang(0) \
            .build()

        response = self.client.docx.v1.document.raw_content(request)

        if response.success():
            return response.data.content
        else:
            raise Exception(f"{response.code}: {response.msg}")

    def save_all_contents(self, contents: List[Dict]):
        """保存所有文档内容"""
        print(f"\n💾 保存文档内容...")

        # 保存合并的文本
        output_file = self.data_dir / 'full_kb_content.txt'

        with open(output_file, 'w', encoding='utf-8') as f:
            for doc in contents:
                f.write(f"{'='*70}\n")
                f.write(f"文档: {doc['title']}\n")
                f.write(f"Token: {doc['obj_token']}\n")
                f.write(f"{'='*70}\n\n")
                f.write(doc['content'])
                f.write(f"\n\n")

        total_chars = sum(doc['length'] for doc in contents)
        print(f"✅ 保存完成: {output_file}")
        print(f"   文档数: {len(contents)}")
        print(f"   总字符: {total_chars:,}")
        print(f"   文件大小: {total_chars / 1024 / 1024:.2f} MB")

        # 保存元数据
        metadata = {
            'total_docs': len(contents),
            'total_chars': total_chars,
            'build_time': time.strftime("%Y-%m-%d %H:%M:%S"),
            'documents': [
                {
                    'title': doc['title'],
                    'obj_token': doc['obj_token'],
                    'length': doc['length']
                }
                for doc in contents
            ]
        }

        metadata_file = self.data_dir / 'full_kb_metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"✅ 元数据已保存: {metadata_file}")

    def _load_progress(self) -> Dict:
        """加载下载进度"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_progress(self, progress: Dict):
        """保存下载进度"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)


def main():
    print("=" * 70)
    print("🚀 飞书完整知识库学习")
    print("=" * 70)

    learner = FullKBLearner()

    # 步骤1: 获取所有节点
    print("\n[步骤 1/3] 获取知识库结构")
    print("-" * 70)
    nodes = learner.get_all_nodes(use_cache=True)

    if not nodes:
        print("❌ 未找到任何文档节点")
        return False

    # 显示统计
    print(f"\n📊 知识库统计:")
    print(f"  文档总数: {len(nodes)}")

    # 询问是否继续
    print(f"\n⚠️  将下载 {len(nodes)} 个文档，预计需要 10-30 分钟")
    print(f"   按 Ctrl+C 可随时中断，下次继续")

    # 可选：限制下载数量（测试用）
    import sys
    if '--test' in sys.argv:
        max_docs = 10
        print(f"\n🧪 测试模式：只下载前 {max_docs} 个文档")
    elif '--limit' in sys.argv:
        idx = sys.argv.index('--limit')
        max_docs = int(sys.argv[idx + 1]) if idx + 1 < len(sys.argv) else None
        print(f"\n📝 限制模式：只下载前 {max_docs} 个文档")
    else:
        max_docs = None

    # 如果不是测试模式，需要确认（仅在交互模式下）
    if (max_docs is None or max_docs > 100) and '--auto' not in sys.argv:
        print()
        print("⚠️  这将需要较长时间")
        print("   建议先运行: python3 learn_full_kb.py --test")
        print("   或添加 --auto 参数自动开始")
        print()
        try:
            input("按 Enter 继续，或 Ctrl+C 取消...")
        except (EOFError, KeyboardInterrupt):
            print("\n已取消")
            return False
    elif max_docs is None:
        print("\n✅ 自动开始完整学习...")

    # 步骤2: 下载所有文档
    print("\n[步骤 2/3] 下载文档内容")
    print("-" * 70)
    contents = learner.download_all_documents(nodes, max_docs=max_docs)

    if not contents:
        print("❌ 未下载任何文档内容")
        return False

    # 步骤3: 保存内容
    print("\n[步骤 3/3] 保存文档内容")
    print("-" * 70)
    learner.save_all_contents(contents)

    print("\n" + "=" * 70)
    print("✅ 完整知识库学习完成！")
    print("=" * 70)
    print(f"\n下一步:")
    print(f"  python3 build_offline_kb_fast.py")
    print(f"\n或使用新文件:")
    print(f"  python3 build_full_kb_index.py")

    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  下载已中断")
        print("   下次运行将从断点继续")
        sys.exit(1)
