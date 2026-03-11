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

def top_k_smallest(arr, k, key=lambda x: x):
    # 如果要求的k太大，直接快速排序给出结果
    if k >= len(arr):
        return quick_sort(arr, key=key)
    if k == 0:
        return []
    # 使用负号变为维护一个大根堆
    max_heap = []
    for item in arr:
        # 前k个元素正常进堆
        if len(max_heap) < k:
            heappush(max_heap, (-key(item), item), key=lambda x: x[0])
        # 后面的元素如果可能，替换最大元素，然后维护堆
        else:
            # 使用一个负号回归原来的key，如果更小，则有下面操作
            if key(item) < -max_heap[0][0]:
                heappop(max_heap, key=lambda x: x[0])
                heappush(max_heap, (-key(item), item), key=lambda x: x[0])
    result = []
    while max_heap:
        result.append(heappop(max_heap, key=lambda x: x[0])[1])
    return result[::-1]

def quick_sort(arr, key=lambda x: x):
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[0]
        left = []
        right = []
        for element in arr[1:]:
            if key(element) <= key(pivot):
                left.append(element)
            else:
                right.append(element)
        return quick_sort(left, key) + [pivot] + quick_sort(right, key)