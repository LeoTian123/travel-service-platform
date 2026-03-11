def natural_merge_sort(arr, key=None, reverse=False):
    """
    自然归并排序，支持 key 函数和 reverse 参数

    参数:
        arr: 待排序的列表
        key: 可选函数，用于从每个元素中提取比较键
        reverse: 若为 True，则降序排序；若为 False，则升序排序（默认）

    返回:
        排序后的列表（原地排序）
    """
    if len(arr) <= 1:
        return arr  # 空列表或只有一个元素的列表已经有序

    # 辅助数组，用于归并操作
    temp = arr.copy()

    while True:
        runs = find_runs(arr, key, reverse)

        # 如果只有一个有序段，说明整个数组已经有序
        if len(runs) == 1:
            break

        # 归并相邻的有序段
        i = 0
        while i < len(runs) - 1:
            start1, end1 = runs[i]
            start2, end2 = runs[i + 1]
            merge(arr, temp, start1, end1, start2, end2, key, reverse)
            # 更新合并后的有序段边界
            runs[i] = (start1, end2)
            # 移除已合并的有序段
            del runs[i + 1]
            i += 1

    return arr


def find_runs(arr, key=None, reverse=False):
    """
    找出数组中的自然有序段

    返回:
        有序段的列表，每个元素是一个元组 (start, end)，表示有序段的起始和结束索引（闭区间）
    """
    if not arr:
        return []

    runs = []
    start = 0
    n = len(arr)

    while start < n:
        # 找到当前有序段的结束位置
        end = start
        if reverse:
            while end + 1 < n and (key(arr[end]) if key else arr[end]) >= (key(arr[end + 1]) if key else arr[end + 1]):
                end += 1
        else:
            while end + 1 < n and (key(arr[end]) if key else arr[end]) <= (key(arr[end + 1]) if key else arr[end + 1]):
                end += 1

        runs.append((start, end))
        start = end + 1

    return runs


def merge(arr, temp, start1, end1, start2, end2, key=None, reverse=False):
    """
    归并两个相邻的有序段

    参数:
        arr: 原始数组
        temp: 辅助数组
        start1, end1: 第一个有序段的起始和结束索引
        start2, end2: 第二个有序段的起始和结束索引
        key: 可选函数，用于从每个元素中提取比较键
        reverse: 若为 True，则降序排序；若为 False，则升序排序
    """
    # 将两个有序段复制到辅助数组
    temp[start1:end2 + 1] = arr[start1:end2 + 1]

    # 指向两个有序段的指针
    ptr1 = start1
    ptr2 = start2

    # 归并结果的指针
    dest = start1

    # 比较并归并
    while ptr1 <= end1 and ptr2 <= end2:
        if reverse:
            if (key(temp[ptr1]) if key else temp[ptr1]) >= (key(temp[ptr2]) if key else temp[ptr2]):
                arr[dest] = temp[ptr1]
                ptr1 += 1
            else:
                arr[dest] = temp[ptr2]
                ptr2 += 1
        else:
            if (key(temp[ptr1]) if key else temp[ptr1]) <= (key(temp[ptr2]) if key else temp[ptr2]):
                arr[dest] = temp[ptr1]
                ptr1 += 1
            else:
                arr[dest] = temp[ptr2]
                ptr2 += 1
        dest += 1

    # 复制剩余元素
    while ptr1 <= end1:
        arr[dest] = temp[ptr1]
        ptr1 += 1
        dest += 1

    while ptr2 <= end2:
        arr[dest] = temp[ptr2]
        ptr2 += 1
        dest += 1


# 测试示例
if __name__ == "__main__":
    # 测试用例1：基本升序排序
    arr1 = [5, 3, 8, 4, 6]
    natural_merge_sort(arr1)
    print("测试用例1:", arr1)  # 输出: [3, 4, 5, 6, 8]

    # 测试用例2：降序排序
    arr2 = [5, 3, 8, 4, 6]
    natural_merge_sort(arr2, reverse=True)
    print("测试用例2:", arr2)  # 输出: [8, 6, 5, 4, 3]

    # 测试用例3：使用key函数排序字符串长度
    arr3 = ["apple", "banana", "cherry", "date"]
    natural_merge_sort(arr3, key=len)
    print("测试用例3:", arr3)  # 输出: ['date', 'apple', 'banana', 'cherry']

    # 测试用例4：降序排序字符串长度
    arr4 = ["apple", "banana", "cherry", "date"]
    natural_merge_sort(arr4, key=len, reverse=True)
    print("测试用例4:", arr4)  # 输出: ['cherry', 'banana', 'apple', 'date']

    # 测试用例5：包含重复元素
    arr5 = [7, 5, 3, 5, 8, 4, 6, 4]
    natural_merge_sort(arr5)
    print("测试用例5:", arr5)  # 输出: [3, 4, 4, 5, 5, 6, 7, 8]

    # 测试用例6：已经有序的数组
    arr6 = [1, 2, 3, 4, 5]
    natural_merge_sort(arr6)
    print("测试用例6:", arr6)  # 输出: [1, 2, 3, 4, 5]

    # 测试用例7：完全逆序的数组
    arr7 = [5, 4, 3, 2, 1]
    natural_merge_sort(arr7)
    print("测试用例7:", arr7)  # 输出: [1, 2, 3, 4, 5]

    # 测试用例8：空数组
    arr8 = []
    natural_merge_sort(arr8)
    print("测试用例8:", arr8)  # 输出: []

    # 测试用例9：包含负数和浮点数
    arr9 = [3.5, -2.1, 0, 4.7, -1.9]
    natural_merge_sort(arr9)
    print("测试用例9:", arr9)  # 输出: [-2.1, -1.9, 0, 3.5, 4.7]