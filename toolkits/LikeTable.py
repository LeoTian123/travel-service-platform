from typing import Dict
from toolkits.IntHashSet import IntHashSet
import pickle


class LikeTable:
    def __init__(self, storage_file="likes.pkl"):
        self.storage_file = storage_file
        self.likes: Dict[int, IntHashSet] = {}  # {user_id: IntHashSet(post_ids)}

        # 尝试加载已有的点赞数据
        try:
            with open(self.storage_file, "rb") as f:
                self.likes = pickle.load(f)
        except FileNotFoundError:
            pass

    def like(self, user_id: int, post_id: int) -> bool:
        """用户点赞帖文"""
        if user_id not in self.likes:
            self.likes[user_id] = IntHashSet()

        if post_id in self.likes[user_id]:
            return False  # 已经点过赞

        self.likes[user_id].add(post_id)
        self._save()
        return True

    def unlike(self, user_id: int, post_id: int) -> bool:
        """用户取消点赞"""
        if user_id not in self.likes or post_id not in self.likes[user_id]:
            return False

        self.likes[user_id].remove(post_id)
        if not self.likes[user_id]:
            del self.likes[user_id]
        self._save()
        return True

    def has_liked(self, user_id: int, post_id: int) -> bool:
        """检查用户是否点过赞"""
        return user_id in self.likes and post_id in self.likes[user_id]

    def get_likes_count(self, post_id: int) -> int:
        """获取帖文的点赞数"""
        count = 0
        for user_likes in self.likes.values():
            if post_id in user_likes:
                count += 1
        return count

    def _save(self):
        """保存到文件"""
        with open(self.storage_file, "wb") as f:
            pickle.dump(self.likes, f)

    def __str__(self):
        res = ''
        for k, v in self.likes.items():
            res += f'{k}: {v}\n'
        return res


if __name__ == "__main__":

    # raw_data = {}
    # with open('../Media/attractions/like_table.pickle', "wb") as f:
    #     pickle.dump(raw_data, f)

    like_table_attractions = LikeTable('../Media/attractions/like_table.pickle')
    print(like_table_attractions)

    # raw_data = {}
    # with open('../Media/journals/like_table.pickle', "wb") as f:
    #     pickle.dump(raw_data, f)

    like_table_journals = LikeTable('../Media/journals/like_table.pickle')
    print(like_table_journals)

    from attractions.attractions_manager import *

    attractions_manager = AttractionsManager('../Media/attractions/main-data.pickle')
    # attractions_manager.update_num_likes(like_table_attractions)


    from journals.journals_manager import *

    journals_manager = JournalsManager('../Media/journals/main-data.pickle')
    # journals_manager.update_num_likes(like_table_journals)

    # id_2_idx = {}
    # for idx,attr in enumerate(attractions_manager.get_attractions()):
    #     id_2_idx[attr['id']] = idx
    # # update_num_journals
    # for jou in journals_manager.get_journals():
    #     attractions_manager._data[id_2_idx[jou['spot_id']]]['num_journals'] += 1
    # attractions_manager._save_data()
