#!/usr/bin/env python3
"""
OpenClaw Skill: 飞书离线知识库检索
"""
import sys
import os
import json
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.config import Config
from retriever.simple_search import SimpleSearchEngine


class FeishuKBSkill:
    """飞书知识库Skill"""

    def __init__(self):
        """初始化Skill"""
        self.skill_dir = Path(__file__).parent
        self.data_dir = self.skill_dir / 'data'

        # 检查是否已构建索引
        if not self._check_index():
            print("❌ 知识库索引未构建")
            print("请先运行: /feishu-kb update")
            self.search_engine = None
        else:
            # 加载配置和搜索引擎
            self.config = Config.load()
            self.search_engine = SimpleSearchEngine(self.config)
            print("✅ 飞书知识库已加载")

    def _check_index(self):
        """检查索引是否存在"""
        required_files = [
            self.data_dir / 'vectors.npz',
            self.data_dir / 'bm25_index.pkl',
            self.data_dir / 'kb_data.db'
        ]
        return all(f.exists() for f in required_files)

    def search(self, query: str, top_k: int = 5, mode: str = 'hybrid', with_images: bool = True):
        """
        搜索知识库

        Args:
            query: 查询内容
            top_k: 返回结果数量
            mode: 检索模式 (vector/keyword/hybrid)
            with_images: 是否检测并标注图片（实时图片理解功能）

        Returns:
            搜索结果
        """
        if not self.search_engine:
            return {
                'error': '知识库未初始化，请先运行 /feishu-kb update'
            }

        try:
            # 文本检索
            results = self.search_engine.search(query, top_k=top_k, mode=mode)

            if not results:
                return {
                    'query': query,
                    'results': [],
                    'message': '未找到相关内容'
                }

            # 图片增强（检测图片引用）
            if with_images:
                results = self.search_engine.enrich_with_images(results, enable_images=True)

            return {
                'query': query,
                'count': len(results),
                'results': results,
                'mode': mode,
                'with_images': with_images
            }

        except Exception as e:
            return {
                'error': f'搜索失败: {str(e)}'
            }

    def update(self):
        """更新知识库"""
        print("🔄 开始更新知识库...")

        try:
            # 1. 获取飞书内容
            print("\n[1/2] 从飞书获取内容...")
            import subprocess
            result = subprocess.run(
                ['python3', 'fetch_wiki_content.py'],
                cwd=self.skill_dir,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                return {
                    'error': f'获取内容失败: {result.stderr}'
                }

            print("✅ 内容获取成功")

            # 2. 构建索引
            print("\n[2/2] 构建离线索引...")
            result = subprocess.run(
                ['python3', 'build_offline_kb_fast.py'],
                cwd=self.skill_dir,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                return {
                    'error': f'构建索引失败: {result.stderr}'
                }

            print("✅ 索引构建成功")

            # 重新加载搜索引擎
            self.config = Config.load()
            self.search_engine = SimpleSearchEngine(self.config)

            return {
                'success': True,
                'message': '知识库更新成功'
            }

        except Exception as e:
            return {
                'error': f'更新失败: {str(e)}'
            }

    def learn(self, url_or_id: str):
        """
        学习单个飞书文档

        Args:
            url_or_id: 文档URL或文档ID

        Returns:
            学习结果
        """
        print(f"📚 学习飞书文档: {url_or_id}")

        try:
            # 1. 获取文档内容
            print("\n[1/3] 获取文档内容...")
            import subprocess
            result = subprocess.run(
                ['python3', 'learn_document.py', url_or_id],
                cwd=self.skill_dir,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                return {
                    'error': f'获取文档失败: {result.stderr}'
                }

            print("✅ 文档获取成功")

            # 提取保存的文档路径（从输出中解析）
            output_lines = result.stdout.split('\n')
            doc_path = None
            for line in output_lines:
                if '文档已保存:' in line:
                    doc_path = line.split('文档已保存:')[1].strip()
                    break

            if not doc_path:
                return {
                    'error': '无法确定文档保存路径'
                }

            # 2. 增量更新索引
            print("\n[2/3] 更新索引...")
            result = subprocess.run(
                ['python3', 'incremental_index.py', doc_path],
                cwd=self.skill_dir,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                return {
                    'error': f'更新索引失败: {result.stderr}'
                }

            print("✅ 索引更新成功")

            # 3. 重新加载搜索引擎
            print("\n[3/3] 重新加载搜索引擎...")
            self.config = Config.load()
            self.search_engine = SimpleSearchEngine(self.config)
            print("✅ 搜索引擎已重新加载")

            return {
                'success': True,
                'message': '文档学习完成',
                'doc_path': doc_path
            }

        except Exception as e:
            return {
                'error': f'学习失败: {str(e)}'
            }

    def status(self):
        """获取知识库状态"""
        try:
            metadata_file = self.data_dir / 'metadata.json'

            if not metadata_file.exists():
                return {
                    'status': 'not_initialized',
                    'message': '知识库未初始化，请运行 /feishu-kb update'
                }

            with open(metadata_file) as f:
                metadata = json.load(f)

            # 获取文件大小
            files = {
                'vectors': self.data_dir / 'vectors.npz',
                'bm25': self.data_dir / 'bm25_index.pkl',
                'database': self.data_dir / 'kb_data.db',
                'content': self.data_dir / 'raw' / 'wiki_content.txt'
            }

            file_sizes = {}
            for name, path in files.items():
                if path.exists():
                    size = path.stat().st_size
                    file_sizes[name] = self._format_size(size)
                else:
                    file_sizes[name] = 'N/A'

            return {
                'status': 'ready',
                'metadata': metadata,
                'files': file_sizes,
                'search_engine': 'loaded' if self.search_engine else 'not_loaded'
            }

        except Exception as e:
            return {
                'error': f'获取状态失败: {str(e)}'
            }

    def _format_size(self, size_bytes):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


def main():
    """Skill入口"""
    import argparse

    parser = argparse.ArgumentParser(description='飞书离线知识库检索')
    parser.add_argument('command', choices=['search', 'update', 'status', 'learn'],
                       help='命令')
    parser.add_argument('args', nargs='*', help='命令参数')
    parser.add_argument('--mode', default='hybrid',
                       choices=['vector', 'keyword', 'hybrid'],
                       help='检索模式')
    parser.add_argument('--top-k', type=int, default=5,
                       help='返回结果数量')
    parser.add_argument('--format', default='text',
                       choices=['text', 'json'],
                       help='输出格式')
    parser.add_argument('--with-images', action='store_true', default=True,
                       help='检测并标注图片内容（默认开启）')
    parser.add_argument('--no-images', action='store_true',
                       help='禁用图片检测（更快）')

    args = parser.parse_args()

    # 初始化Skill
    skill = FeishuKBSkill()

    # 执行命令
    if args.command == 'search':
        if not args.args:
            print("❌ 请提供查询内容")
            sys.exit(1)

        query = ' '.join(args.args)
        with_images = not args.no_images  # 默认开启，除非指定 --no-images
        result = skill.search(query, top_k=args.top_k, mode=args.mode, with_images=with_images)

        if args.format == 'json':
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_search_result(result)

    elif args.command == 'update':
        result = skill.update()

        if args.format == 'json':
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            if 'error' in result:
                print(f"❌ {result['error']}")
            else:
                print(f"✅ {result['message']}")

    elif args.command == 'status':
        result = skill.status()

        if args.format == 'json':
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_status(result)

    elif args.command == 'learn':
        if not args.args:
            print("❌ 请提供文档URL或ID")
            print("\n用法:")
            print("  /feishu-kb learn <文档URL或ID>")
            print("\n示例:")
            print("  /feishu-kb learn https://xxx.feishu.cn/docx/xxxxx")
            print("  /feishu-kb learn doxcnxxxxxx")
            sys.exit(1)

        url_or_id = args.args[0]
        result = skill.learn(url_or_id)

        if args.format == 'json':
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            if 'error' in result:
                print(f"\n❌ {result['error']}")
            else:
                print(f"\n✅ {result['message']}")
                if 'doc_path' in result:
                    print(f"   文档: {result['doc_path']}")


def print_search_result(result):
    """打印搜索结果（文本格式）"""
    if 'error' in result:
        print(f"❌ {result['error']}")
        return

    print(f"\n📚 查询: {result['query']}")
    print(f"模式: {result.get('mode', 'hybrid')}")
    print(f"结果数: {result.get('count', 0)}")
    print("=" * 70)

    if not result['results']:
        print(result.get('message', '未找到结果'))
        return

    for i, item in enumerate(result['results'], 1):
        print(f"\n{i}. 【分数: {item['score']:.3f}】")
        print(f"   标题: {item.get('doc_title', 'N/A')}")
        print(f"   内容: {item['content'][:200]}...")
        print()


def print_status(result):
    """打印状态信息（文本格式）"""
    if 'error' in result:
        print(f"❌ {result['error']}")
        return

    if result['status'] == 'not_initialized':
        print(f"⚠️  {result['message']}")
        return

    print("\n📊 知识库状态")
    print("=" * 70)

    metadata = result['metadata']
    print(f"构建时间: {metadata['build_time']}")
    print(f"文档块数: {metadata['chunk_count']}")
    print(f"向量维度: {metadata['vector_dimension']}")
    print(f"模型: {metadata['model']}")

    print(f"\n文件大小:")
    for name, size in result['files'].items():
        print(f"  {name}: {size}")

    print(f"\n搜索引擎: {result['search_engine']}")
    print()


if __name__ == '__main__':
    main()
