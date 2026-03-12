"""
检索功能测试
"""
import pytest
from src.utils.config import Config
from src.retriever.search_engine import SearchEngine


class TestSearch:
    """检索测试"""

    @pytest.fixture
    def config(self):
        """加载配置"""
        return Config.load()

    @pytest.fixture
    def search_engine(self, config):
        """创建搜索引擎"""
        return SearchEngine(config)

    def test_vector_search(self, search_engine):
        """测试向量检索"""
        results = search_engine.search(
            query="产品功能",
            top_k=5,
            mode='vector'
        )

        assert isinstance(results, list)
        if results:
            assert 'doc_id' in results[0]
            assert 'content' in results[0]
            assert 'score' in results[0]

    def test_keyword_search(self, search_engine):
        """测试关键词检索"""
        results = search_engine.search(
            query="API 文档",
            top_k=5,
            mode='keyword'
        )

        assert isinstance(results, list)

    def test_hybrid_search(self, search_engine):
        """测试混合检索"""
        results = search_engine.search(
            query="技术架构",
            top_k=5,
            mode='hybrid'
        )

        assert isinstance(results, list)

    def test_get_stats(self, search_engine):
        """测试统计信息"""
        stats = search_engine.get_stats()

        assert 'total_docs' in stats
        assert 'total_chunks' in stats
        assert isinstance(stats['total_docs'], int)
