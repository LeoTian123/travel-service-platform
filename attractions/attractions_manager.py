import os
import pickle
from copy import deepcopy
from typing import List, Dict, Any, Optional
from toolkits import heapqueue, Aho_Corasick
from toolkits.FuzzyMatching import FuzzySearcher
from toolkits.MergeSort import natural_merge_sort
from toolkits.IntHashSet import IntHashSet
import math
from collections import defaultdict


class AttractionsManager:
    """
    管理景点数据的类，负责读取、筛选、排序和分页操作。
    """
    def __init__(self, data_file_path: str):
        """
        初始化 AttractionsManager。

        :param data_file_path: 景点数据文件的路径
        """
        self.data_file_path = data_file_path
        self._data: Optional[List[Dict[str, Any]]] = None

    def _load_data(self) -> None:
        """
        从文件加载景点数据到内存。
        """
        try:
            with open(self.data_file_path, 'rb') as f:
                self._data = pickle.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"景点数据文件不存在: {self.data_file_path}")
        except pickle.PickleError as e:
            raise pickle.PickleError(f"景点数据文件解析失败: {e}")

    def _save_data(self) -> None:
        """
        将景点数据保存到文件。如果需要频繁修改数据，可以调用此方法。
        """
        if self._data is not None:
            with open(self.data_file_path, 'wb') as f:
                pickle.dump(self._data, f)

    def get_attractions(
        self,
        keyword: str = '',
        spot_type: str = '',
        sort_type: str = '',
        sort_direction: str = 'asc'
    ) -> List[Dict[str, Any]]:
        """
        获取筛选、排序后的景点数据。

        :param keyword: 关键词筛选
        :param spot_type: 景点类型筛选
        :param sort_type: 排序类型（如 'comments', 'likes'）
        :param sort_direction: 排序方向（'asc' 或 'desc'）
        :return: 筛选和排序后的景点列表
        """
        if self._data is None:
            self._load_data()

        # 复制数据以避免修改原始数据
        filtered_data = self._data.copy()

        # 应用筛选条件
        if spot_type:
            filtered_data = [
                spot for spot in filtered_data
                if spot.get('type', '').lower() == spot_type.lower()
            ]

        use_fuzzy_search = False
        score_map = {}   # 存储 {item_id: score}
        if keyword:
            use_fuzzy_search = True
            keyword_list = keyword.split(' ')

            # # 模式1. 严格匹配
            # filtered_data = [
            #     spot for spot in filtered_data
            #     if self._match_keyword(spot, keyword_list)
            # ]

            # 景点模块采取模式2. 模糊匹配
            search_results = {}  # 存储 {item_id: [item, total_score]}
            for each in keyword_list:
                searcher = FuzzySearcher(filtered_data)
                for item, score in searcher.get_score(each):
                    item_id = item['id']
                    if item_id not in search_results:
                        search_results[item_id] = [item, score]  # 首次遇到该item
                    else:
                        search_results[item_id][1] += score  # 累加分数
            # 最终结果：将字典转换为列表
            final_results = list(search_results.values())

            final_len = 15 * len(keyword_list)
            final_results_sorted = heapqueue.top_k_largest(final_results, key=lambda x: x[1], k=final_len)
            filtered_data = [x[0] for x in final_results_sorted]
            filtered_data_score = [x[1] for x in final_results_sorted]

            # 构建ID到分数的映射
            for i in range(final_len):
                score_map[filtered_data[i]['id']] = filtered_data_score[i]

        # 应用排序
        if not sort_type:
            if not sort_direction:
                pass
            else:
                if sort_direction == 'rev':
                    filtered_data.reverse()
        else:
            if not (sort_direction == 'rev'):
                # 默认是从大到小
                top_k_function = heapqueue.top_k_largest
            else:
                # 也可以选择从小到大
                top_k_function = heapqueue.top_k_smallest

            if sort_type == 'comments':
                def sort_key(x):
                    base_score = x.get('num_comment_quna', 0)
                    if use_fuzzy_search:
                        return base_score * score_map.get(x['id'], 1.0)**2
                    return base_score

            elif sort_type == 'likes':
                def sort_key(x):
                    num_likes = x.get('num_likes', 0)
                    num_journals = x.get('num_journals', 0)
                    base_score = num_likes + num_journals * 2
                    if use_fuzzy_search:
                        return base_score * score_map.get(x['id'], 1.0)**2
                    return base_score

            else:
                def sort_key(x):
                    return 0

            filtered_data = top_k_function(
                filtered_data,
                k=10,
                key=sort_key
            )

        return filtered_data

    def _match_keyword(
        self,
        spot: Dict[str, Any],
        keyword_list: List[str]
    ) -> bool:
        """
        检查景点是否匹配关键词

        Args:
            spot (dict): 景点数据字典
            keyword (str): 搜索关键词

        Returns:
            bool: 是否匹配
        """
        for keyword in keyword_list:
            keyword = keyword.lower()
        text = ''.join([
            spot['cnName'].lower(),
            spot['enName'].lower(),
            (spot.get('description', '')).lower()
        ])
        automaton = Aho_Corasick.build_automaton(keyword_list)
        matches = Aho_Corasick.aho_corasick_search(text, automaton)
        if matches:
            return True
        return False

    def get_attractions_paginated(
        self,
        keyword: str = '',
        spot_type: str = '',
        sort_type: str = '',
        sort_direction: str = 'asc',
        page_num: int = 0,
        page_size: int = 30
    ) -> Dict[str, Any]:
        """
        获取分页后的景点数据，并包含总页数信息。

        :param keyword: 关键词筛选
        :param spot_type: 景点类型筛选
        :param sort_type: 排序类型（如 'comments', 'likes'）
        :param sort_direction: 排序方向（'asc' 或 'desc'）
        :param page_num: 当前页码（从0开始）
        :param page_size: 每页数量
        :return: 包含景点列表和分页信息的字典
        """
        filtered_data = self.get_attractions(keyword, spot_type, sort_type, sort_direction)

        total_num = len(filtered_data)
        index_left = page_size * page_num
        index_right = page_size * (page_num + 1)

        if index_right > total_num:
            index_right = total_num
        if index_left >= total_num:
            return {
                'data': [],
                'length': 0,
                'current_page': page_num,
                'page_size': page_size,
                'total_pages': (total_num + page_size - 1) // page_size
            }

        # 获取当前页数据
        retlist = filtered_data[index_left:index_right]

        return {
            'data': deepcopy(retlist),
            'length': len(retlist),
            'current_page': page_num,
            'page_size': page_size,
            'total_pages': (total_num + page_size - 1) // page_size
        }

    def update_num_likes(self, like_table) -> None:
        """
        按照点赞表重新更新所有的num_likes。
        是一个测试时期构建数据使用的函数。

        :param like_table: 点赞表
        """
        for index, attraction in enumerate(self.get_attractions()):
            attraction['num_likes'] = 0
        for index, attraction in enumerate(self.get_attractions()):
            spot_id = attraction['id']
            for k, v in like_table.likes.items():
                if spot_id in v:
                    attraction['num_likes'] += 1
        self._save_data()

    def like_attraction(self, spot_id: int) -> bool:
        """
        点赞景点。

        :param spot_id: 要点赞的景点ID
        :return: 是否点赞成功
        """
        if self._data is None:
            self._load_data()

        for spot in self._data:
            if spot['id'] == spot_id:
                spot['num_likes'] += 1
                self._save_data()
                return True

        return False

    def unlike_attraction(self, spot_id: int) -> bool:
        """
        取消点赞景点。

        :param spot_id: 要取消点赞的景点ID
        :return: 是否取消点赞成功
        """
        if self._data is None:
            self._load_data()

        for spot in self._data:
            if spot['id'] == spot_id:
                current_likes = spot['num_likes']
                if current_likes > 0:
                    spot['num_likes'] = current_likes - 1
                    self._save_data()
                    return True
                return False

        return False

    def get_user_liked_attractions(self, user_id, like_table) -> List[Dict[str, Any]]:
        """
        获取指定用户已点赞的所有景点数据。

        :param user_id: 用户ID
        :param like_table: 点赞表
        :return: 已点赞的景点列表
        """
        if self._data is None:
            self._load_data()

        # 筛选出用户已点赞的景点
        user_liked_attractions = []
        for spot in self._data:
            if like_table.has_liked(user_id=user_id, post_id=spot['id']):
                user_liked_attractions.append(spot)

        return user_liked_attractions

    def get_UBCF(self, like_table, user_id, num_recommendations=10):
        """
        基于用户协同过滤生成景点推荐

        :param like_table: LikeTable实例，包含用户点赞数据
        :param user_id: 当前用户ID
        :param num_recommendations: 需要推荐的景点数量
        :return: 推荐的景点列表，每个景点包含'recommendation_score'字段
        """
        # 获取目标用户的点赞列表
        target_user_likes = like_table.likes.get(user_id, IntHashSet())
        if not target_user_likes:
            return []

        # 计算用户相似度并找到最相似的K个用户
        user_similarities = defaultdict(float)
        for other_user_id, other_likes in like_table.likes.items():
            if other_user_id == user_id:
                continue

            # 计算Jaccard相似度
            intersection = len(target_user_likes.intersection(other_likes))
            union = len(target_user_likes) + len(other_likes) - intersection

            if union > 0:
                similarity = intersection / union
                user_similarities[other_user_id] = similarity

        # 找到最相似的K个用户（这里K设为5，可以根据需要调整）
        similar_users = sorted(user_similarities.items(), key=lambda x: x[1], reverse=True)[:5]

        # 基于相似用户的喜好生成推荐
        recommendation_scores = defaultdict(float)
        for other_user_id, similarity in similar_users:
            other_user_likes = like_table.likes[other_user_id]
            for post_id in other_user_likes:
                if post_id not in target_user_likes:  # 只推荐目标用户没有点赞过的景点
                    recommendation_scores[post_id] += similarity

        # 按推荐分数排序并获取前N个推荐
        recommended_post_ids = sorted(recommendation_scores.items(), key=lambda x: x[1], reverse=True)[
                               :num_recommendations]

        # 获取推荐景点的详细信息
        if self._data is None:
            self._load_data()

        # 构建景点ID到景点数据的映射
        id_to_attraction = {attraction['id']: attraction for attraction in self._data}

        # 筛选出推荐的景点，并添加推荐分数
        recommended_attractions = []
        for post_id, score in recommended_post_ids:
            if post_id in id_to_attraction:
                attraction = id_to_attraction[post_id].copy()  # 创建副本，避免修改原始数据
                attraction['recommendation_score'] = score  # 添加推荐分数
                recommended_attractions.append(attraction)

        return recommended_attractions
