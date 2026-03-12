"""
查询优化器
- 查询预处理和清洗
- 中文分词和停用词过滤
- 查询扩展（同义词）
- 查询改写
"""
from typing import List, Dict, Set
import re
import jieba
from loguru import logger


class QueryOptimizer:
    """查询优化器"""

    # 中文停用词列表（常见的无意义词）
    STOP_WORDS = {
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
        '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
        '你', '会', '着', '没有', '看', '好', '自己', '这'
    }

    # 产品相关同义词映射
    SYNONYMS = {
        'POS机': ['POS', 'pos机', 'pos', '收款机', '刷卡机'],
        '扫码王': ['扫码设备', '扫码枪', '扫码器'],
        '通道': ['支付通道', '收款通道', '渠道'],
        '费率': ['手续费', '费用', '成本'],
        '商户': ['商家', '店铺', '门店'],
        '收款': ['收钱', '付款', '支付']
    }

    def __init__(self, config):
        """
        初始化查询优化器

        Args:
            config: 配置对象
        """
        self.config = config
        self.enable_segmentation = True
        self.enable_stopwords = True
        self.enable_expansion = True

        logger.info("查询优化器初始化完成")
        logger.info(f"  - 中文分词: {self.enable_segmentation}")
        logger.info(f"  - 停用词过滤: {self.enable_stopwords}")
        logger.info(f"  - 查询扩展: {self.enable_expansion}")

    def optimize_query(self, query: str) -> Dict[str, any]:
        """
        优化查询

        Args:
            query: 原始查询

        Returns:
            优化后的查询信息，包含：
            - original: 原始查询
            - cleaned: 清洗后的查询
            - tokens: 分词结果
            - expanded: 扩展后的查询词
            - reformulated: 改写后的查询
        """
        if not query or not query.strip():
            return {
                'original': query,
                'cleaned': '',
                'tokens': [],
                'expanded': [],
                'reformulated': query
            }

        logger.debug(f"优化查询: '{query}'")

        # 1. 清洗查询
        cleaned = self._clean_query(query)

        # 2. 中文分词
        tokens = self._segment_query(cleaned)

        # 3. 停用词过滤
        filtered_tokens = self._filter_stopwords(tokens)

        # 4. 查询扩展（同义词）
        expanded = self._expand_query(filtered_tokens)

        # 5. 查询改写
        reformulated = self._reformulate_query(cleaned, filtered_tokens)

        result = {
            'original': query,
            'cleaned': cleaned,
            'tokens': filtered_tokens,
            'expanded': expanded,
            'reformulated': reformulated,
            'all_terms': list(set(filtered_tokens + expanded))  # 所有查询词（去重）
        }

        logger.debug(f"优化完成: {result}")
        return result

    def _clean_query(self, query: str) -> str:
        """
        清洗查询

        Args:
            query: 原始查询

        Returns:
            清洗后的查询
        """
        # 转为小写（英文）
        query = query.lower()

        # 移除多余空白
        query = re.sub(r'\s+', ' ', query)

        # 移除特殊字符（保留中文、英文、数字）
        query = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', ' ', query)

        # 再次清理空白
        query = query.strip()

        return query

    def _segment_query(self, query: str) -> List[str]:
        """
        中文分词

        Args:
            query: 查询文本

        Returns:
            分词结果
        """
        if not self.enable_segmentation:
            return [query]

        # 使用jieba分词
        tokens = jieba.cut(query)
        tokens = [t.strip() for t in tokens if t.strip()]

        return tokens

    def _filter_stopwords(self, tokens: List[str]) -> List[str]:
        """
        过滤停用词

        Args:
            tokens: 分词结果

        Returns:
            过滤后的词列表
        """
        if not self.enable_stopwords:
            return tokens

        filtered = [
            token for token in tokens
            if token not in self.STOP_WORDS and len(token) > 1
        ]

        return filtered

    def _expand_query(self, tokens: List[str]) -> List[str]:
        """
        查询扩展（添加同义词）

        Args:
            tokens: 查询词列表

        Returns:
            扩展词列表
        """
        if not self.enable_expansion:
            return []

        expanded = []

        for token in tokens:
            # 查找同义词
            for canonical, synonyms in self.SYNONYMS.items():
                if token in synonyms or token == canonical:
                    # 添加规范词
                    expanded.append(canonical)
                    # 添加部分同义词
                    expanded.extend(synonyms[:2])
                    break

        # 去重
        expanded = list(set(expanded) - set(tokens))

        if expanded:
            logger.debug(f"查询扩展: {tokens} → +{expanded}")

        return expanded

    def _reformulate_query(self, query: str, tokens: List[str]) -> str:
        """
        查询改写

        将疑问句转换为陈述句等

        Args:
            query: 原始查询
            tokens: 分词结果

        Returns:
            改写后的查询
        """
        # 移除疑问词
        question_words = ['如何', '怎么', '怎样', '什么', '哪些', '为什么', '是否', '能否']

        reformulated = query
        for qw in question_words:
            reformulated = reformulated.replace(qw, '')

        # 清理空白
        reformulated = re.sub(r'\s+', ' ', reformulated).strip()

        # 如果改写后为空，使用原查询
        if not reformulated:
            reformulated = query

        return reformulated

    def generate_multiple_queries(self, query: str) -> List[str]:
        """
        生成多个查询变体

        用于multi-query检索策略

        Args:
            query: 原始查询

        Returns:
            查询变体列表
        """
        optimized = self.optimize_query(query)

        queries = [
            optimized['original'],  # 原始查询
            optimized['reformulated'],  # 改写查询
        ]

        # 如果有扩展词，生成扩展查询
        if optimized['expanded']:
            expanded_query = ' '.join(optimized['all_terms'])
            queries.append(expanded_query)

        # 去重
        queries = list(set(q for q in queries if q))

        logger.debug(f"生成 {len(queries)} 个查询变体")
        return queries

    def add_synonyms(self, canonical: str, synonyms: List[str]):
        """
        添加自定义同义词

        Args:
            canonical: 规范词
            synonyms: 同义词列表
        """
        self.SYNONYMS[canonical] = synonyms
        logger.info(f"添加同义词: {canonical} = {synonyms}")

    def add_stopwords(self, words: List[str]):
        """
        添加停用词

        Args:
            words: 停用词列表
        """
        self.STOP_WORDS.update(words)
        logger.info(f"添加停用词: {words}")
