# 文件名: fuzzy_search.py
from pypinyin import pinyin, Style
import jieba

"""
模糊搜索的技术方向：
1基于字符串匹配的算法
编辑距离（Levenshtein Distance）：计算两个字符串的最小修改次数（插入、删除、替换），适合短文本或关键词匹配。
前缀匹配（Prefix Matching）：如Trie树，快速定位以输入为前缀的字符串（适合景区名称首字母搜索）。
通配符匹配：支持*和?的模糊模式（如*长城*匹配含“长城”的描述）。
2基于概率与统计的方法
N-Gram模型：将字符串拆分为连续子串（如“长城”→“长”、“城”、“长城”），计算子串重叠度。
TF-IDF + 余弦相似度：通过关键词权重和向量夹角衡量文本相似性（适合长描述匹配）。
3基于语义理解的算法
词嵌入（Word2Vec/BERT）：将文本映射到向量空间，计算语义相似度（适合复杂语义场景，但实现复杂）。
拼音纠错与转换：结合拼音库处理输入错误（如“zhangcheng”→“长城”）。

这里采用了 编辑距离算法：
1.汉字编辑距离		匹配景区汉语名称、描述
2.字符编辑距离		匹配景区汉语名称的拼音、英文名称
"""


def levenshtein_distance(s1, s2):
    """
    计算两个字符串之间的编辑距离（Levenshtein Distance）
    :param s1: 字符串1
    :param s2: 字符串2
    :return: 最小编辑操作次数（插入、删除、替换）
    """
    m, n = len(s1), len(s2)

    # 创建 (m+1) x (n+1) 的二维数组
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # 初始化边界条件（第一行和第一列）
    for i in range(m + 1):
        dp[i][0] = i  # 将 s1[:i] 转换为空字符串 s2[:0]，需要 i 次删除
    for j in range(n + 1):
        dp[0][j] = j  # 将空字符串 s1[:0] 转换为 s2[:j]，需要 j 次插入

    # 动态规划填表
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                # 字符相同，无需操作，继承左上角的值
                dp[i][j] = dp[i - 1][j - 1]
            else:
                # 取左（插入）、上（删除）、左上（替换）中的最小值 +1
                dp[i][j] = 1 + min(
                    dp[i][j - 1],  # 插入 s2[j-1] 到 s1
                    dp[i - 1][j],  # 删除 s1[i-1]
                    dp[i - 1][j - 1]  # 替换 s1[i-1] 为 s2[j-1]
                )

    return dp[m][n]


class FuzzySearcher:
    def __init__(self, data, pinyin_style=Style.NORMAL, weights=None):
        """
        初始化模糊搜索器
        :param data: 数据列表，格式示例 [{'id':1, 'name':'长城', 'description':'...'}, ...]
        :param pinyin_style: 拼音风格（默认不带声调）
        :param weights: 权重配置 [汉字权重, 拼音权重, Bi-Gram权重]
        """
        self.data = data
        self.pinyin_style = pinyin_style

        # 设置默认权重（汉字:0.5，拼音:0.5）
        self.weights = weights if weights else [0.5, 0.5]

        # 预处理拼音
        self._preprocess_data()

    def _preprocess_data(self):
        """预处理"""
        self.hanzi_map = {}
        self.pinyin_map = {}
        self.bigram_map = {}

        for item in self.data:
            # 存储汉语名字拆分开
            self.hanzi_map[item['id']] = jieba.lcut(item['cnName'], cut_all=True)

            # 存储汉语名字拆分开的拼音、英文拆分开
            self.pinyin_map[item['id']] = [self._to_pinyin(x) for x in self.hanzi_map[item['id']]]
            self.pinyin_map[item['id']] += [x.lower() for x in item['enName'].split(' ')]

            # 存储描述拆分开
            self.hanzi_map[item['id']] += jieba.lcut(item['description'].replace('，', ' ').replace('。', ' '))

    def _to_pinyin(self, text):
        """转换单个文本为拼音"""
        pinyin_list = pinyin(text, style=self.pinyin_style)
        return ''.join([item[0] for item in pinyin_list])

    def _calc_scores(self, query, item):
        """计算单个项目的综合得分"""
        han_score = 0
        py_score = 0

        # 1. 汉字编辑距离得分
        if not query.isascii():
            han_score_list = []
            for each_q in jieba.lcut(query, cut_all=True):
                for each_d in self.hanzi_map[item['id']]:
                    han_score_list.append(
                        1 / (levenshtein_distance(each_q, each_d) + 1)
                    )
            han_score = max(han_score_list)

        # 2. 字符编辑距离得分
        query_pinyin = [self._to_pinyin(x) for x in jieba.lcut(query)]
        query_pinyin = [x.lower() for x in query_pinyin]
        py_score_list = []
        for each_q in query_pinyin:
            for each_d in self.pinyin_map[item['id']]:
                py_score_list.append(
                    1 - levenshtein_distance(each_q, each_d) / max(len(each_q), len(each_d))
                )
        py_score = max(py_score_list)

        # 加权综合
        return (
                self.weights[0] * han_score +
                self.weights[1] * py_score
        )

    def search(self, query, top_k=10):
        """
        执行搜索
        :param query: 查询字符串
        :param top_k: 返回结果数量
        :return: 排序后的结果列表，格式 [(item_dict, score), ...]
        """
        scores = []
        for item in self.data:
            score = self._calc_scores(query, item)
            scores.append((item, score))

        # 按得分排序并返回前top_k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def get_score(self, query):
        """
        类似search，但是返回所有结果按照[item,score]的列表
        :param query: 查询字符串
        :return: 按照[item,score]的列表
        """
        scores = []
        for item in self.data:
            score = self._calc_scores(query, item)
            scores.append([item,score])

        return scores

if __name__ == '__main__':
    import pickle
    from toolkits.MergeSort import natural_merge_sort
    data_file_path = '../Media/attractions/main-data.pickle'
    with open(data_file_path, 'rb') as f:
        data = pickle.load(f)

    search_results = {}  # 存储 {item_id: [item, total_score]}
    for each in ['长成', 'bupT']:
        searcher = FuzzySearcher(data)
        for item, score in searcher.get_score(each):
            item_id = item['id']
            if item_id not in search_results:
                search_results[item_id] = [item, score]  # 首次遇到该item
            else:
                search_results[item_id][1] += score  # 累加分数

    # 最终结果：将字典转换为列表
    final_results = list(search_results.values())
    final_results.sort(key=lambda x: x[1], reverse=True)

    for e, score in final_results[:30]:
        print(e['cnName'], e['enName'], e['description'])
        print(score)
        print()
