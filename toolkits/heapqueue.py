"""
小根堆函数：
heappush
heappop
heapify
top_k_largest
大根堆函数：
heappush_max
heappop_max
heapify_max
top_k_largest
其他：
quick_sort
"""


def heappush(heap, item, key=lambda x: x):
    # 最小堆
    heap.append(item)
    i = len(heap) - 1
    while i > 0:
        parent = (i - 1) // 2
        if key(heap[i]) >= key(heap[parent]):
            break
        heap[i], heap[parent] = heap[parent], heap[i]
        i = parent


def heappop(heap, key=lambda x: x):
    # 最小堆
    if not heap:
        return None
    if len(heap) == 1:
        return heap.pop()
    result = heap[0]
    heap[0] = heap.pop()
    i = 0
    n = len(heap)
    while True:
        left = 2 * i + 1
        right = 2 * i + 2
        smallest = i
        if left < n and key(heap[left]) < key(heap[smallest]):
            smallest = left
        if right < n and key(heap[right]) < key(heap[smallest]):
            smallest = right
        if smallest == i:
            break
        heap[i], heap[smallest] = heap[smallest], heap[i]
        i = smallest
    return result


def heapify(arr, key=lambda x: x):
    # 最小堆
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        current = i
        while True:
            left = 2 * current + 1
            right = 2 * current + 2
            smallest = current
            if left < n and key(arr[left]) < key(arr[smallest]):
                smallest = left
            if right < n and key(arr[right]) < key(arr[smallest]):
                smallest = right
            if smallest == current:
                break
            arr[current], arr[smallest] = arr[smallest], arr[current]
            current = smallest


def top_k_largest(arr, k, key=lambda x: x):
    # 如果要求的k太大，直接快速排序给出结果
    if k >= len(arr):
        return quick_sort(arr, key=key, reverse=True)
    if k == 0:
        return []
    # 使用最小堆
    min_heap = []
    for item in arr:
        # 前k个元素正常进堆
        if len(min_heap) < k:
            heappush(min_heap, (key(item), item), key=lambda x: x[0])
        # 后面的元素如果可能，替换最小元素，然后维护堆
        else:
            if key(item) > min_heap[0][0]:
                heappop(min_heap, key=lambda x: x[0])
                heappush(min_heap, (key(item), item), key=lambda x: x[0])
    # 将堆中的元素按从大到小的顺序返回
    result = []
    while min_heap:
        result.append(heappop(min_heap, key=lambda x: x[0])[1])
    return result[::-1]


'''
 本来top_k_smallest使用加一个负号模拟大根堆的方法，但是有两个问题导致后来决定修改
 1.逻辑复杂，不好维护，但不致命
 2.不能排序元组对象，这很致命，因为项目排序日期的时候确实用到了这一点
 最终决定写一下大根堆，完善top_k_smallest
'''


def heappush_max(heap, item, key=lambda x: x):
    # 最大堆
    heap.append(item)
    i = len(heap) - 1
    while i > 0:
        parent = (i - 1) // 2
        if key(heap[i]) <= key(heap[parent]):  # 注意这里是 <=，与最小堆相反
            break
        heap[i], heap[parent] = heap[parent], heap[i]
        i = parent


def heappop_max(heap, key=lambda x: x):
    # 最大堆
    if not heap:
        return None
    if len(heap) == 1:
        return heap.pop()
    result = heap[0]
    heap[0] = heap.pop()
    i = 0
    n = len(heap)
    while True:
        left = 2 * i + 1
        right = 2 * i + 2
        largest = i
        if left < n and key(heap[left]) > key(heap[largest]):  # 注意这里是 >
            largest = left
        if right < n and key(heap[right]) > key(heap[largest]):  # 注意这里是 >
            largest = right
        if largest == i:
            break
        heap[i], heap[largest] = heap[largest], heap[i]
        i = largest
    return result


def heapify_max(arr, key=lambda x: x):
    # 最大堆
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        current = i
        while True:
            left = 2 * current + 1
            right = 2 * current + 2
            largest = current
            if left < n and key(arr[left]) > key(arr[largest]):  # 注意这里是 >
                largest = left
            if right < n and key(arr[right]) > key(arr[largest]):  # 注意这里是 >
                largest = right
            if largest == current:
                break
            arr[current], arr[largest] = arr[largest], arr[current]
            current = largest


def top_k_smallest(arr, k, key=lambda x: x):
    # 如果要求的k太大，直接快速排序给出结果
    if k >= len(arr):
        return quick_sort(arr, key=key)
    if k == 0:
        return []
    # 使用最大堆
    max_heap = []
    for item in arr:
        if len(max_heap) < k:
            heappush_max(max_heap, (key(item), item), key=lambda x: x[0])  # 使用最大堆
        else:
            if key(item) < max_heap[0][0]:  # 直接比较 key
                heappop_max(max_heap, key=lambda x: x[0])
                heappush_max(max_heap, (key(item), item), key=lambda x: x[0])

    # 提取结果（按 key 升序排序）
    result = [item for (key_val, item) in sorted(max_heap, key=lambda x: x[0])]
    return result


def quick_sort(arr, key=lambda x: x, reverse=False):
    # 如果 reverse=True，则按降序排序；否则按升序排序。
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[0]
        left = []
        right = []
        for element in arr[1:]:
            if (key(element) > key(pivot)) if reverse else (key(element) <= key(pivot)):
                left.append(element)
            else:
                right.append(element)
        if reverse:
            return quick_sort(left, key, reverse) + [pivot] + quick_sort(right, key, reverse)
        else:
            return quick_sort(left, key) + [pivot] + quick_sort(right, key)
