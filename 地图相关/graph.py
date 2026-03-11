from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union
from PIL import Image
import heapqueue
from itertools import permutations

@dataclass
class NodeAttributes:
    """
    节点属性的数据类。
    使用 __slots__ 优化内存布局。
    """
    __slots__ = (
        'pos',
        'prototype',
        'type',
        'name',
    )  # 定义节点属性
    __annotations__ = {
        'pos': Optional[Tuple[float, float]],
        'prototype': Optional[str],
        'type': Optional[str],
        'name': Optional[str]
    }  # 类型注解


@dataclass
class EdgeAttributes:
    """
    边属性的数据类。
    使用 __slots__ 优化内存布局。
    """
    __slots__ = (
        'vehicle',
        'distance',
        'crowdedness',
        'walk_time',
        'bike_time'
    )  # 定义边属性
    __annotations__ = {
        'vehicle': Optional[str],
        'distance': Optional[float],
        'crowdedness': Optional[float],
        'walk_time': Optional[float],
        'bike_time': Optional[float]
    }  # 类型注解


class Graph:
    def __init__(
            self,
            num_nodes: int,
            bike_speed: float,
            walk_speed: float = 5,
    ):
        """
        初始化图数据结构。
        :param num_nodes: 图中节点的数量。
        """
        self.num_nodes = num_nodes

        # 节点属性表：一个数组，索引是节点编号，值是节点属性（NodeAttributes 对象）
        self.nodes: List[Optional[NodeAttributes]] = [None for _ in range(num_nodes)]

        # 边属性表：一个数组，索引是起点节点编号，值是一个字典，键是邻点编号，值是边属性（EdgeAttributes 对象）
        # 限定了两个点的大小顺序
        self.edges: List[Dict[int, EdgeAttributes]] = [{} for _ in range(num_nodes)]

        # 无属性节点表：
        self.node_list: List[int] = list(range(num_nodes))

        # 无属性邻接表：所有的点作为索引，元素是邻接的点的列表
        self.adjacency_list: List[List[int]] = [[] for _ in range(num_nodes)]

        # 路径速度
        self.bike_speed = bike_speed
        self.walk_speed = walk_speed

    def add_node(
            self,
            node_id: int,
            pos: Optional[Tuple[float, float]] = None,
            prototype: Optional[str] = None,
            node_type: Optional[str] = None,
            name: Optional[str] = None
    ):
        """
        添加一个节点及其属性。
        :param node_id: 节点编号
        :param pos: 节点的位置
        :param prototype: 节点的原型
        :param node_type: 节点的类型
        :param name: 节点的名称
        """
        if node_id < 0 or node_id >= self.num_nodes:
            raise ValueError("Node index out of range")

        # 创建节点属性对象
        node_attrs = NodeAttributes(
            pos=pos,
            prototype=prototype,
            type=node_type,
            name=name
        )

        # 更新节点属性表
        self.nodes[node_id] = node_attrs

    def add_edge(
            self,
            from_node: int,
            to_node: int,
            vehicle: Optional[str] = None,
            distance: Optional[float] = None,
            crowdedness: Optional[float] = None,
    ):
        """
        添加一条边及其属性。
        :param from_node: 起点节点编号
        :param to_node: 终点节点编号
        :param vehicle: 边的交通工具类型
        :param distance: 边的距离
        :param crowdedness: 边的拥挤程度
        """
        if from_node < 0 or from_node >= self.num_nodes or to_node < 0 or to_node >= self.num_nodes:
            raise ValueError("Node index out of range")

        # 构造路上的两个时间
        walk_time = float('inf')
        bike_time = float('inf')
        if vehicle == 'walk' or vehicle == 'both':
            real_walk_speed = self.walk_speed * crowdedness
            # 时间单位为分钟
            walk_time = (distance / 1000) / real_walk_speed * 60
        if vehicle == 'bike' or vehicle == 'both':
            real_bike_speed = self.bike_speed * crowdedness
            # 时间单位为分钟
            bike_time = (distance / 1000) / real_bike_speed * 60

        # 创建边属性对象
        edge_attrs = EdgeAttributes(
            vehicle=vehicle,
            distance=distance,
            crowdedness=crowdedness,
            walk_time=walk_time,
            bike_time=bike_time
        )

        # 添加边到邻接表，正反都需要添加
        self.adjacency_list[from_node].append(to_node)
        self.adjacency_list[to_node].append(from_node)

        # 添加边到边属性表，限定大小顺序
        from_node, to_node = sorted([from_node, to_node])
        self.edges[from_node][to_node] = edge_attrs

    def get_node_attributes(self, node: int) -> Optional[NodeAttributes]:
        """
        获取某个节点的属性。更加安全。
        :param node: 节点编号
        :return: 节点属性对象
        """
        if node < 0 or node >= self.num_nodes:
            raise ValueError("Node index out of range")
        return self.nodes[node]

    def get_edge_attributes(self, from_node: int, to_node: int) -> Optional[EdgeAttributes]:
        """
        获取某条边的属性。更加安全。
        :param from_node: 起点节点编号
        :param to_node: 终点节点编号
        :return: 边属性对象，如果边不存在则返回 None
        """
        if from_node < 0 or from_node >= self.num_nodes or to_node < 0 or to_node >= self.num_nodes:
            raise ValueError("Node index out of range")

        # 这是要注意顺序的
        from_node, to_node = sorted([from_node, to_node])
        return self.edges[from_node].get(to_node, None)

    def get_neighbors(self, node: int) -> List[int]:
        """
        获取某个节点的所有邻居。更加安全。
        :param node: 节点编号
        :return: 邻居节点及其边属性的字典
        """
        if node < 0 or node >= self.num_nodes:
            raise ValueError("Node index out of range")
        return self.adjacency_list[node]

    def Nodes(self, data: str) -> List[Any]:
        """
        根据属性名获取节点属性值的列表。
        :param data: 属性名
        :return: 包含节点属性值的列表
        """
        if not isinstance(data, str):
            raise ValueError("The 'data' parameter must be a string representing a node attribute name.")
        if hasattr(self.nodes[0], data):
            return [getattr(self.nodes[node], data) for node in self.node_list]
        raise AttributeError(f"Node attribute '{data}' does not exist")

    def Edges(self, data: str) -> Dict[Tuple[int, int], Any]:
        """
        根据属性名获取边属性值的字典。
        :param data: 属性名
        :return: {edge: attribute_value} 的字典
        """
        if not isinstance(data, str):
            raise ValueError("The 'data' parameter must be a string representing an edge attribute name.")
        edge_dict = {}
        for from_node, neighbors in enumerate(self.edges):
            for to_node, attrs in neighbors.items():
                edge = (from_node, to_node)
                if hasattr(attrs, data):
                    edge_dict[edge] = getattr(attrs, data)
                else:
                    raise AttributeError(f"Edge attribute '{data}' does not exist for edge {edge}.")
        return edge_dict

    def __str__(self):
        """
        打印图的字符串表示。
        :return: 图的字符串表示
        """
        result = "Nodes:\n"
        for i, attrs in enumerate(self.nodes):
            result += f"  Node {i}: {attrs}\n"

        result += "\nEdges:\n"
        for from_node, neighbors in enumerate(self.edges):
            for to_node, attrs in neighbors.items():
                result += f"  {from_node} -> {to_node}: {attrs}\n"
        return result

    def visualize_graph(
            self,
            ax,
            path: Optional[List[int]]=None,
            mode: Optional[str] = None,  # distance, time, walk_time, bike_time
            lable: Optional[str] = None   # id, name
    ):

        ax.set_title("Visualization of My Graph")

        pos = self.Nodes(data='pos')

        # 画边
        path_formed = []
        if path is not None:
            for i in range(len(path)-1):
                path_formed.append(sorted([path[i], path[i+1]]))
        for (u, v), vehicle in self.Edges(data='vehicle').items():
            if vehicle == 'walk' or vehicle == 'both':
                arc = 0
                color = 'black'
                width = 1

                if path is not None:
                    if sorted([u,v]) in path_formed:
                        if mode == 'walk_time' or mode == 'distance':
                            width = 10
                        elif mode == 'time':
                            if vehicle == 'walk':
                                width = 10

                ax.annotate("",
                            xy=pos[u], xycoords='data',
                            xytext=pos[v], textcoords='data',
                            arrowprops=dict(arrowstyle="-",
                                            color=color,
                                            linewidth=width,
                                            shrinkA=5, shrinkB=5,
                                            patchA=None, patchB=None,
                                            connectionstyle=f"arc3,rad={0.1 * arc}"
                                            ),
                            )
            if vehicle == 'bike' or vehicle == 'both':
                arc = 0.3
                color = 'purple'
                width = 1

                if path is not None:
                    if sorted([u,v]) in path_formed:
                        if mode == 'bike_time' or mode == 'distance':
                            width = 10
                        elif mode == 'time':
                            width = 10


                ax.annotate("",
                            xy=pos[u], xycoords='data',
                            xytext=pos[v], textcoords='data',
                            arrowprops=dict(arrowstyle="-",
                                            color=color,
                                            linewidth=width,
                                            shrinkA=5, shrinkB=5,
                                            patchA=None, patchB=None,
                                            connectionstyle=f"arc3,rad={0.1 * arc}"
                                            ),
                            )

        # 画点
        def draw_custom_nodes(graph, pos):
            scale = 15
            for node in graph.node_list:
                x, y = pos[node]
                prototype = graph.nodes[node].prototype
                type = graph.nodes[node].type

                image_path = rf'节点图片\{prototype}\{type}.png'

                image = Image.open(image_path)
                # 调整图片大小（使用抗锯齿采样）
                image_resized = image.resize(
                    (2 * scale, 2 * scale),
                    resample=Image.Resampling.LANCZOS
                )

                # 显示图像（将PIL对象直接传入plt.imshow）
                ax.imshow(image_resized, extent=(x - scale, x + scale, y - scale, y + scale), aspect='auto')

        draw_custom_nodes(self, pos)

        # 画标签
        if lable is None:
            name_labels = self.node_list
        else:
            if lable == 'name':
                name_labels = self.Nodes(data='name')
            else:
                name_labels = self.node_list

        for node in self.node_list:
            label = name_labels[node]
            if label is not None:
                ax.text(*(pos[node]), label, horizontalalignment='center', verticalalignment='center')

        # 显示坐标轴和网格线
        ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
        ax.grid(True)

    def dijkstra(self, source, target=None, weight='weight') -> Union[
        Tuple[Dict[int, float], Dict[int, List[int]]],
        Tuple[float, List[int]]
    ]:
        """
        单源头 Dijkstra 算法实现，支持返回从起点到目标节点的最短路径和距离。

        参数:
            G (nx.Graph): 输入的图。
            source (node): 起点。
            target (node, optional): 目标节点。如果为 None，则返回从起点到所有节点的最短路径。
            weight (str, optional):  取值只能是 distance, time, walk_time, bike_time

        返回:
            如果指定了 target，返回 (distance, path)，格式 Tuple[float, List[int]]
            如果未指定 target，返回 (distances, paths)，格式 Tuple[Dict[int, float], Dict[int, List[int]]]
        """
        # 如果起点和目标节点相同，直接返回距离为 0 和路径为 [target]
        if target == source:
            return 0, [target]

        # 使用权重函数解析权重属性

        def _weight_function(u, v):
            edge_attrs = self.get_edge_attributes(u, v)
            if edge_attrs is None:
                return None
            # time属性需要单独处理
            if weight == 'time':
                return min(edge_attrs.walk_time, edge_attrs.bike_time)
            # 其余属性（walk_time，bike_time，distance）不需要处理
            return getattr(edge_attrs, weight, None)

        # 初始化路径字典，记录从起点到每个节点的路径
        paths = {source: [source]}

        # 调用核心 Dijkstra 算法
        dist = self._dijkstra([source], _weight_function, paths=paths)

        # 如果未指定目标节点，返回所有节点的最短距离和路径
        if target is None:
            return dist, paths

        # 如果指定了目标节点，尝试返回最短距离和路径，该语境下必然成功
        if target in dist:
            return dist[target], paths[target]
        return float('inf'), []

    def _dijkstra(self, sources, weight, paths=None):
        """
        核心 Dijkstra 算法实现，计算从起点到其他节点的最短距离。

        参数:
            G (nx.Graph): 输入的图。
            sources (list): 起点列表（单源头时只有一个起点）。
            weight (function): 权重函数，用于计算边的权重。
            paths (dict, optional): 记录从起点到每个节点的路径。

        返回:
            dist (dict): 从起点到每个节点的最短距离。
        """
        # 初始化优先队列（堆）和相关数据结构
        push = heapqueue.heappush
        pop = heapqueue.heappop
        dist = {}  # 存储从起点到每个节点的最短距离
        seen = {}  # 存储已经处理过的节点及其当前已知的最短距离
        fringe = []  # 堆（优先队列），用于存储待处理的节点

        # 初始化起点
        for source in sources:
            seen[source] = 0  # 起点的初始距离为 0
            push(fringe, (0, source))  # 将起点加入堆

        # 主循环：从堆中取出当前距离最小的节点
        while fringe:
            (d, v) = pop(fringe)  # 弹出堆顶元素 (distance, node)
            if v in dist:
                continue  # 如果节点已经被处理过，跳过

            # 记录当前节点的最短距离
            dist[v] = d

            # 遍历当前节点的所有邻居
            for u in self.get_neighbors(v):
                cost = weight(v, u)  # 计算从 v 到 u 的边的权重
                if cost is None:
                    continue  # 如果边不可通行，跳过

                # 计算从起点经过 v 到 u 的总距离
                vu_dist = dist[v] + cost

                # 如果找到更短的路径，更新距离并加入堆
                if u not in seen or vu_dist < seen[u]:
                    seen[u] = vu_dist  # 更新节点 u 的最短距离
                    push(fringe, (vu_dist, u))  # 将节点 u 加入堆

                    # 如果需要记录路径，更新路径信息
                    if paths is not None:
                        paths[u] = paths[v] + [u]

        # 返回从起点到所有节点的最短距离
        return dist

    def shortest_path_with_visited_nodes(self, start, visited_nodes, weight='time'):
        """
        从起点出发，经过所有待游览节点，并回到起点的最短路径。

        参数:
            G (Graph): 输入的图。
            start (node): 起点。
            visited_nodes (list): 待游览节点列表。

        返回:
            path (list): 最短路径的节点序列。
            total_time (float): 路径的总时间。
        """
        # Step 1: 构建子图，包含起点和待游览节点
        subgraph_nodes = [start] + visited_nodes

        # Step 2: 用字典存储子图的边信息
        subgraph = {}
        for u in subgraph_nodes:
            subgraph[u] = {}
            for v in subgraph_nodes:
                if u != v:
                    (length, path) = self.dijkstra(u, target=v, weight=weight)
                    subgraph[u][v] = {'time': length, 'path': path}

        # Step 3: 将问题转化为 TSP，求解最短路径
        # 待游览节点的排列组合
        min_time = float('inf')
        best_path = None

        # 遍历所有可能的顺序（暴力搜索，适用于待游览节点数量较少的情况）
        for perm in permutations(visited_nodes):
            current_time = 0
            current_path = [start]

            # 按照排列顺序遍历待游览节点
            for i in range(len(perm)):
                u = current_path[-1]
                v = perm[i]
                current_time += subgraph[u][v]['time']
                current_path.append(v)

            # 返回起点
            current_time += subgraph[current_path[-1]][start]['time']
            current_path.append(start)

            # 更新最短路径
            if current_time < min_time:
                min_time = current_time
                best_path = current_path

        best_path_formed = [(best_path[i], best_path[i + 1]) for i in range(len(best_path) - 1)]
        best_path_extended = []
        for u, v in best_path_formed:
            path = subgraph[u][v]['path']
            if path[0] == u:
                best_path_extended += path[:-1]
            else:
                best_path_extended += list(reversed(path))[:-1]
        best_path_extended.append(start)

        return best_path, best_path_extended, min_time

    def radar_search(self, source, k, weight='time', node_type=None):
        (list_distances, _) = self.dijkstra(source, weight=weight)
        index = list(range(self.num_nodes))
        if node_type is not None:
            index_typed = []
            for i in index:
                if self.get_node_attributes(i).type == node_type:
                    index_typed.append(i)
            index = index_typed
        top_k_index = heapqueue.top_k_smallest(index, k, key=lambda x: list_distances[x])

        return top_k_index



# 示例用法
if __name__ == "__main__":
    g = Graph(4, 15)

    g.add_node(0, (803.6720768991145, 697.015740995268), 'building0', '地标0', '办公楼0')
    g.add_node(1, (772.2447692966574, 657.6128923003433), 'cross1', '地标1', '办公楼1')
    g.add_node(2, (325.183322026747, 722.4521152615054), 'building2', '办公楼2', '办公楼2')
    g.add_node(3, (280.93450968738074, 712.1792213475359), 'building3', '地标3', '办公楼3')

    g.add_edge(0, 1, 'both', 123.123, 0.954)
    g.add_edge(0, 2, 'walk', 223.123, 0.254)
    g.add_edge(1, 2, 'bike', 323.123, 0.354)
    g.add_edge(1, 3, 'both', 423.123, 0.454)

    print(g)
