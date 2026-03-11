import os
import pickle
from copy import deepcopy
from typing import List, Dict, Any, Optional
from django.core.files.uploadedfile import UploadedFile
from datetime import datetime
import uuid
from toolkits import heapqueue
from toolkits import heapqueue, Aho_Corasick
from toolkits.ImageCompressor import ImageCompressor


class JournalsManager:
    """
    管理日记数据的类，负责读取、筛选、排序、分页以及点赞相关操作。
    """
    def __init__(self, data_file_path: str):
        """
        初始化 JournalsManager。

        :param data_file_path: 日记数据文件的路径
        """
        self.data_file_path = data_file_path
        self._data: Optional[List[Dict[str, Any]]] = None

    def _load_data(self) -> None:
        """
        从文件加载日记数据到内存。
        """
        try:
            data, _ = ImageCompressor.decompress_image(self.data_file_path + '.hcmp')
            self._data = pickle.loads(data)
        except FileNotFoundError:
            raise FileNotFoundError(f"日记数据文件不存在: {self.data_file_path}")
        except pickle.PickleError as e:
            raise pickle.PickleError(f"日记数据文件解析失败: {e}")

    def _save_data(self) -> None:
        """
        将日记数据保存到文件。如果需要频繁修改数据，可以调用此方法。
        """
        if self._data is not None:
            with open(self.data_file_path, 'wb') as f:
                pickle.dump(self._data, f)
            ImageCompressor.compress_image(self.data_file_path, self.data_file_path + '.hcmp')

    def get_journals(
        self,
        keyword: str = '',
        spot_id: str = '',
        uploader_id: str = '',
        sort_type: str = '',
        sort_direction: str = 'asc'
    ) -> List[Dict[str, Any]]:
        """
        获取筛选、排序后的日记数据。

        :param keyword: 关键词筛选
        :param spot_id: 景点ID筛选
        :param uploader_id: 上传者ID筛选
        :param sort_type: 排序类型（如 'likes', 'date'）
        :param sort_direction: 排序方向（'asc' 或 'desc'）
        :return: 筛选和排序后的日记列表
        """
        if self._data is None:
            self._load_data()

        # 复制数据以避免修改原始数据
        filtered_data = self._data.copy()

        # 应用筛选条件
        if spot_id:
            filtered_data = [
                journal for journal in filtered_data
                if str(journal.get('spot_id')) == spot_id
            ]

        if uploader_id:
            filtered_data = [
                journal for journal in filtered_data
                if str(journal.get('user_id')) == uploader_id
            ]

        if keyword:
            keyword_list = keyword.split()

            # 日记搜索使用模式1. 严格匹配
            filtered_data = [
                journal for journal in filtered_data
                if self._match_keyword(journal, keyword_list)
            ]

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
            if sort_type == 'likes':
                filtered_data = top_k_function(filtered_data, 10, lambda x: x.get('num_likes', 0))
            elif sort_type == 'date':
                # 将日期字符串转换为datetime对象进行排序
                filtered_data = top_k_function(filtered_data, 10, lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))

        return filtered_data

    def _match_keyword(
        self,
        journal: Dict[str, Any],
        keyword_list: List[str]
    ) -> bool:
        """
        检查日记是否匹配关键词。

        Args:
            journal (dict): 日记数据字典
            keyword_list (list): 搜索关键词列表

        Returns:
            bool: 是否匹配
        """
        for keyword in keyword_list:
            keyword = keyword.lower()
        text = ''.join([
            journal['title'].lower(),
            journal['content'].lower(),
        ])
        automaton = Aho_Corasick.build_automaton(keyword_list)
        matches = Aho_Corasick.aho_corasick_search(text, automaton)
        if matches:
            return True
        return False

    def get_journals_paginated(
        self,
        keyword: str = '',
        spot_id: str = '',
        uploader_id: str = '',
        sort_type: str = '',
        sort_direction: str = 'asc',
        page_num: int = 0,
        page_size: int = 30
    ) -> Dict[str, Any]:
        """
        获取分页后的日记数据，并包含总页数信息。

        :param keyword: 关键词筛选
        :param spot_id: 景点ID筛选
        :param uploader_id: 上传者ID筛选
        :param sort_type: 排序类型（如 'likes', 'date'）
        :param sort_direction: 排序方向（'asc' 或 'desc'）
        :param page_num: 当前页码（从0开始）
        :param page_size: 每页数量
        :return: 包含日记列表和分页信息的字典
        """
        filtered_data = self.get_journals(keyword, spot_id, uploader_id, sort_type, sort_direction)

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

        :param like_table: 点赞表实例
        """
        for journal in self.get_journals():
            journal['num_likes'] = 0
        for journal in self.get_journals():
            journal_id = journal['journal_id']
            for k, v in like_table.likes.items():
                if journal_id in v:
                    journal['num_likes'] += 1
        self._save_data()

    def like_journal(self, journal_id: int) -> bool:
        """
        点赞日记。

        :param journal_id: 要点赞的日记ID
        :return: 是否点赞成功
        """
        if self._data is None:
            self._load_data()

        for journal in self._data:
            if journal['journal_id'] == journal_id:
                journal['num_likes'] += 1
                self._save_data()
                return True

        return False

    def unlike_journal(self, journal_id: int) -> bool:
        """
        取消点赞日记。

        :param journal_id: 要取消点赞的日记ID
        :return: 是否取消点赞成功
        """
        if self._data is None:
            self._load_data()

        for journal in self._data:
            if journal['journal_id'] == journal_id:
                current_likes = journal['num_likes']
                if current_likes > 0:
                    journal['num_likes'] = current_likes - 1
                    self._save_data()
                    return True
                return False

        return False

    def get_user_liked_journals(self, user_id: int, like_table) -> List[Dict[str, Any]]:
        """
        获取指定用户已点赞的所有日记数据。

        :param user_id: 用户ID
        :param like_table: 点赞表实例
        :return: 已点赞的日记列表
        """
        if self._data is None:
            self._load_data()

        # 筛选出用户已点赞的日记
        user_liked_journals = []
        for journal in self._data:
            if like_table.has_liked(user_id=user_id, post_id=journal['journal_id']):
                user_liked_journals.append(journal)

        return user_liked_journals

    def add_journal(
            self,
            title: str,
            date: str,
            spot_id: int,
            content: str,
            user_id: int,
            imgs: List[UploadedFile],  # 这里传入的是图片文件对象列表（request.FILES.getlist('imgs')）
            base_img_path: str,  # 这必须传，涉及到运行时环境的问题
    ) -> dict:
        """
        添加新日记到数据文件

        :param title: 日记标题
        :param date: 日期字符串(YYYY-MM-DD)
        :param spot_id: 景点ID
        :param content: 日记内容
        :param user_id: 用户ID
        :param imgs: 图片文件对象列表
        :param base_img_path: 图片存储路径
        :return: 是否添加成功
        """
        if self._data is None:
            self._load_data()

        # 确定新的journal_id
        if not self._data:
            new_journal_id = 1
        else:
            new_journal_id = max(j['journal_id'] for j in self._data) + 1

        # 处理图片并保存到磁盘
        img_names = []
        for i, img in enumerate(imgs):
            # 生成图片名: img{journal_id}_{index}_{timestamp}_{random_str}.{ext}
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            random_str = uuid.uuid4().hex[:4]
            ext = img.name.split('.')[-1] if '.' in img.name else 'jpg'
            img_name = f"img{new_journal_id}_{i}_{timestamp}_{random_str}.{ext}"
            img_names.append(img_name)

            # 实际保存图片文件
            img_path = os.path.join(base_img_path, img_name)
            # os.makedirs(os.path.dirname(img_path), exist_ok=True)  # 确保目录存在
            with open(img_path, 'wb+') as f:
                for chunk in img.chunks():
                    f.write(chunk)

        # 创建新日记数据
        new_journal = {
            'journal_id': new_journal_id,
            'title': title,
            'date': date,
            'spot_id': spot_id,
            'imgs': img_names,  # 只存文件名
            'content': content,
            'user_id': user_id,
            'num_likes': 0
        }

        # 添加到数据列表
        if self._data is None:
            self._data = []
        self._data.append(new_journal)
        self._save_data()
        return new_journal
