from collections import deque, defaultdict

"""
Aho-Corasick 算法是一种高效的多模式字符串匹配算法，由 Alfred V. Aho 和 Margaret J. Corasick 在 1975 年提出。
该算法能够在 O(n + m + z) 的时间复杂度内完成匹配，其中：
n 是主字符串的长度，
m 是所有模式串的总长度，
z 是匹配的总次数。
Aho-Corasick 算法广泛应用于关键词过滤、敏感词检测、病毒扫描、拼写检查等领域。

算法概述
Aho-Corasick 算法通过构建一个有限状态自动机（Finite State Automaton, FSA），将所有模式串整合到该自动机中。
在匹配过程中，只需线性扫描主字符串，利用自动机的状态转移和失败指针机制，高效地找到所有模式串的出现位置。

算法核心组成部分
1.Trie 树（前缀树）：
用于存储所有模式串，每个节点代表一个字符，路径表示一个字符串的前缀。
叶子节点通常标记模式串的结束，并存储该模式串的信息。
2.失败指针（Failure Link）：
类似于 KMP 算法中的部分匹配表（Partial Match Table），用于在当前状态匹配失败时，快速跳转到另一个状态继续匹配。
失败指针指向当前状态的最长后缀所在的状态。
3.输出函数（Output Function）：
每个状态可能对应一个或多个模式串的结束位置，输出函数记录这些模式串。
"""


class AhoNode:
    def __init__(self):
        self.goto = defaultdict(AhoNode)  # 子节点
        self.fail = None  # 失败指针
        self.output = []  # 输出列表


def build_automaton(patterns):
    root = AhoNode()

    # 构建 Trie 树
    for pattern in patterns:
        node = root
        for char in pattern:
            node = node.goto[char]
        node.output.append(pattern)

    # 构建失败指针
    queue = deque()

    # 第一层子节点的失败指针指向根节点
    for child in root.goto.values():
        child.fail = root
        queue.append(child)

    # BFS 遍历构建失败指针
    while queue:
        current_node = queue.popleft()

        for char, child in current_node.goto.items():
            queue.append(child)

            fail_node = current_node.fail
            while fail_node is not None and char not in fail_node.goto:
                fail_node = fail_node.fail
            child.fail = fail_node.goto[char] if fail_node and char in fail_node.goto else root
            child.output += child.fail.output

    return root


def aho_corasick_search(text, root):
    current = root
    matches = []

    for i, char in enumerate(text):
        # 沿着失败指针转移，直到找到匹配的子节点或回到根节点
        while current is not None and char not in current.goto:
            current = current.fail
        if current is None:
            current = root
            continue
        current = current.goto[char]

        # 收集所有匹配的模式串
        if current.output:
            for pattern in current.output:
                matches.append((i - len(pattern) + 1, pattern))

    return matches


# 示例使用
if __name__ == "__main__":
    patterns = ["he", "she", "his", "hers"]
    text = "ushersaskedehushehersuiheoihih"

    automaton = build_automaton(patterns)
    matches = aho_corasick_search(text, automaton)

    if matches:
        print("匹配到的模式串及其位置：")
        for pos, pattern in matches:
            print(f"模式串 '{pattern}' 出现在位置 {pos}")
    else:
        print("未匹配到任何模式串。")