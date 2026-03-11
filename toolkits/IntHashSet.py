class IntHashSet:
    def __init__(self, initial_capacity=8):
        self.capacity = initial_capacity
        self.size = 0
        self.table = [None] * self.capacity  # 哈希表存储 (key, None) 或 (key, deleted_flag)
        self.DELETED = object()  # 标记已删除的槽位

    def _hash(self, key: int) -> int:
        """计算哈希值并取模"""
        return hash(key) % self.capacity

    def _resize(self):
        """扩容哈希表"""
        old_table = self.table
        self.capacity *= 2
        self.table = [None] * self.capacity
        self.size = 0  # 重置 size，重新插入时会更新

        for item in old_table:
            if item is not None and item != self.DELETED:
                self.add(item[0])

    def add(self, key: int) -> None:
        """添加元素"""
        if self.size >= 0.7 * self.capacity:
            self._resize()

        index = self._hash(key)
        original_index = index

        while True:
            if self.table[index] is None or self.table[index] == self.DELETED:
                # 空槽位或已删除的槽位，直接插入
                self.table[index] = (key, None)
                self.size += 1
                return
            elif self.table[index][0] == key:
                # 已存在，无需重复插入
                return

            # 线性探测
            index = (index + 1) % self.capacity
            if index == original_index:
                raise RuntimeError("Hash table is full (shouldn't happen with resizing)")

    def remove(self, key: int) -> bool:
        """删除元素"""
        index = self._hash(key)
        original_index = index

        while True:
            if self.table[index] is None:
                # 未找到
                return False
            elif self.table[index] == self.DELETED:
                # 跳过已删除的槽位
                pass
            elif self.table[index][0] == key:
                # 找到元素，标记为 DELETED
                self.table[index] = self.DELETED
                return True

            # 线性探测
            index = (index + 1) % self.capacity
            if index == original_index:
                break  # 遍历完整个表

        return False

    def contains(self, key: int) -> bool:
        """检查元素是否存在"""
        index = self._hash(key)
        original_index = index

        while True:
            if self.table[index] is None:
                # 未找到
                return False
            elif self.table[index] == self.DELETED:
                # 跳过已删除的槽位
                pass
            elif self.table[index][0] == key:
                # 找到元素
                return True

            # 线性探测
            index = (index + 1) % self.capacity
            if index == original_index:
                break  # 遍历完整个表

        return False

    def get_all(self) -> list:
        """获取所有元素（按插入顺序，不保证顺序）"""
        result = []
        for item in self.table:
            if item is not None and item != self.DELETED:
                result.append(item[0])
        return result

    def __str__(self) ->str:
        res = str(self.get_all())
        return '{' + res[1:-1] + '}'

    def __len__(self) -> int:
        """返回集合大小"""
        return self.size

    def __contains__(self, key: int) -> bool:
        """支持 `in` 操作符"""
        return self.contains(key)

    def __iter__(self):
        """支持迭代功能"""
        return iter(self.get_all())
    def intersection(self, other: 'IntHashSet') -> 'IntHashSet':
        """获取两个集合的交集"""
        result = IntHashSet()
        for key in self:
            if key in other:
                result.add(key)
        return result


if __name__ == '__main__':
    # 测试 IntHashSet
    hs = IntHashSet()

    # 添加元素
    hs.add(1)
    hs.add(2)
    hs.add(3)
    hs.add(9)  # 哈希冲突测试

    for i in range(10):
        print(i, i in hs)

    # 删除元素
    hs.remove(2)
    print(2 in hs)  # False

    # 检查大小
    print(len(hs))  # 2 (1 和 3)

    # 获取所有元素（顺序可能不同）
    print(hs.get_all())  # [1, 3] 或 [3, 1]（取决于哈希冲突处理）

    # 扩容问题
    print(len(hs), hs.get_all(), hs.capacity)
    hs.add(10)
    hs.add(11)
    hs.add(12)
    hs.add(13)
    print(len(hs), hs.get_all(), hs.capacity)

    s = IntHashSet()
    s.add(1)
    s.add(2)
    s.add(3)
    print(s.intersection(hs))