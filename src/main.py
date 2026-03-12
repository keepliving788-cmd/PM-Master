#!/usr/bin/env python3
"""
飞书产品知识库离线检索 - 主入口
"""
import sys
import click
from pathlib import Path
from loguru import logger

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent))

from indexer.index_manager import IndexManager
from retriever.search_engine import SearchEngine
from utils.config import Config


@click.group()
@click.pass_context
def cli(ctx):
    """飞书产品知识库离线检索工具"""
    ctx.ensure_object(dict)

    # 初始化配置
    config = Config.load()
    ctx.obj['config'] = config

    # 配置日志
    logger.remove()
    logger.add(
        sys.stderr,
        level=config.logging['level'],
        format=config.logging['format']
    )


@cli.command()
@click.option('--full', is_flag=True, help='全量索引（清空重建）')
@click.option('--force', is_flag=True, help='强制重建')
@click.pass_context
def index(ctx, full, force):
    """构建知识库索引"""
    config = ctx.obj['config']
    logger.info("开始构建索引...")

    try:
        manager = IndexManager(config)

        if full or force:
            logger.info("执行全量索引构建")
            result = manager.build_full_index(force=force)
        else:
            logger.info("执行增量索引构建")
            result = manager.build_incremental_index()

        logger.success(f"索引构建完成！")
        logger.info(f"总文档数: {result['total_docs']}")
        logger.info(f"新增文档: {result['new_docs']}")
        logger.info(f"更新文档: {result['updated_docs']}")
        logger.info(f"总耗时: {result['elapsed_time']:.2f}秒")

    except Exception as e:
        logger.error(f"索引构建失败: {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def sync(ctx):
    """同步飞书知识库最新内容"""
    config = ctx.obj['config']
    logger.info("开始同步知识库...")

    try:
        manager = IndexManager(config)
        result = manager.sync()

        logger.success("同步完成！")
        logger.info(f"新增: {result['added']}, 更新: {result['updated']}, 删除: {result['deleted']}")

    except Exception as e:
        logger.error(f"同步失败: {e}")
        sys.exit(1)


@cli.command()
@click.argument('query')
@click.option('--top-k', default=5, help='返回结果数量')
@click.option('--mode', type=click.Choice(['vector', 'keyword', 'hybrid']),
              default='hybrid', help='检索模式')
@click.option('--threshold', default=0.7, help='相似度阈值')
@click.pass_context
def search(ctx, query, top_k, mode, threshold):
    """检索知识库内容"""
    config = ctx.obj['config']

    try:
        engine = SearchEngine(config)
        results = engine.search(
            query=query,
            top_k=top_k,
            mode=mode,
            threshold=threshold
        )

        if not results:
            logger.warning("未找到相关结果")
            return

        # 输出结果
        click.echo(f"\n找到 {len(results)} 个相关结果：\n")

        for i, result in enumerate(results, 1):
            click.echo(f"{'='*80}")
            click.echo(f"[{i}] {result['title']}")
            click.echo(f"相关度: {result['score']:.3f} | 文档ID: {result['doc_id']}")
            click.echo(f"\n{result['content'][:300]}...")
            click.echo(f"\n链接: {result['url']}")
            click.echo()

    except Exception as e:
        logger.error(f"检索失败: {e}")
        sys.exit(1)


@cli.command()
@click.argument('doc_id')
@click.pass_context
def view(ctx, doc_id):
    """查看文档详情"""
    config = ctx.obj['config']

    try:
        engine = SearchEngine(config)
        doc = engine.get_document(doc_id)

        if not doc:
            logger.error(f"文档不存在: {doc_id}")
            return

        click.echo(f"\n{'='*80}")
        click.echo(f"标题: {doc['title']}")
        click.echo(f"文档ID: {doc['doc_id']}")
        click.echo(f"创建时间: {doc['created_at']}")
        click.echo(f"更新时间: {doc['updated_at']}")
        click.echo(f"作者: {doc['author']}")
        click.echo(f"链接: {doc['url']}")
        click.echo(f"\n{'='*80}")
        click.echo(f"\n{doc['content']}\n")

    except Exception as e:
        logger.error(f"查看文档失败: {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def stats(ctx):
    """显示知识库统计信息"""
    config = ctx.obj['config']

    try:
        engine = SearchEngine(config)
        stats = engine.get_stats()

        click.echo(f"\n{'='*80}")
        click.echo("知识库统计信息")
        click.echo(f"{'='*80}\n")

        click.echo(f"总文档数: {stats['total_docs']}")
        click.echo(f"总块数: {stats['total_chunks']}")
        click.echo(f"总字符数: {stats['total_chars']:,}")
        click.echo(f"平均每文档字符数: {stats['avg_chars_per_doc']:.0f}")
        click.echo(f"\n最后更新: {stats['last_updated']}")
        click.echo(f"索引版本: {stats['index_version']}")
        click.echo(f"存储大小: {stats['storage_size']}")

        if stats.get('top_documents'):
            click.echo(f"\n热门文档:")
            for i, doc in enumerate(stats['top_documents'][:5], 1):
                click.echo(f"  {i}. {doc['title']} (访问: {doc['access_count']})")

        click.echo()

    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    cli()
