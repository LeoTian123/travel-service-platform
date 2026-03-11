import numpy as np
import networkx as nx
from scipy.spatial import Delaunay
import random
import os

def generate_random_points(n, extent=None):
    if extent is None:
        extent = [0, 1000, 0, 1000]
    x1, x2, y1, y2 = extent
    x = np.random.rand(n)*(x2-x1) + x1
    y = np.random.rand(n)*(y2-y1) + y1
    return np.column_stack((x, y))


def delaunay_triangulation(points):
    """生成Delaunay三角剖分"""
    G = nx.Graph()

    tri = Delaunay(points)
    for simplex in tri.simplices:
        G.add_edge(simplex[0], simplex[1])
        G.add_edge(simplex[0], simplex[2])
        G.add_edge(simplex[1], simplex[2])
    return G


def kruskal_mst(G):
    """Kruskal算法生成随机的最小生成树"""
    edges = list(G.edges())
    random.shuffle(edges)

    mst = nx.Graph()
    parent = {v: v for v in G.nodes()}

    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u

    def union(u, v):
        u_root = find(u)
        v_root = find(v)
        if u_root != v_root:
            parent[v_root] = u_root

    for u, v in edges:
        if find(u) != find(v):
            union(u, v)
            mst.add_edge(u, v)
    return mst


def union_mst_edge(G_delaunay, num_msts):
    all_edges = []
    for _ in range(num_msts):
        mst = kruskal_mst(G_delaunay.copy())
        all_edges.extend(list(mst.edges()))
    merged_edges = list(set(all_edges))
    return merged_edges


def generate_graph(n=150, num_msts=2, extent=None):
    """生成多MST并集图，一个多重图"""
    points = generate_random_points(n, extent)
    G_delaunay = delaunay_triangulation(points)

    G = nx.Graph()

    # 第一次添加边
    merged_edges_walk = union_mst_edge(G_delaunay, num_msts)
    G.add_edges_from(merged_edges_walk, vehicle='walk')

    # 第二次添加边
    merged_edges_bike = union_mst_edge(G_delaunay, num_msts)
    for u, v in merged_edges_bike:
        if G.has_edge(u, v):
            G.edges[u, v]['vehicle'] = 'both'
        else:
            G.add_edge(u, v, vehicle='bike')

    for i in range(n):
        G.nodes[i]['pos'] = (points[i,0], points[i,1])
    def distance(p, q):
        return ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5
    for u,v in G.edges:
        G.edges[(u,v)]['distance'] = distance(G.nodes[u]['pos'], G.nodes[v]['pos'])

    return G

# 时间单位为 每公里小时
walk_speed = 5
bike_speed = 15
def add_crowdedness_to_edges(G):
    """
    为多重图MG中的每条边添加归一化的"拥挤度"属性

    参数:
    MG (networkx.MultiGraph): 输入的多重图

    返回:
    networkx.MultiGraph: 添加了边属性后的图
    """
    if not G.edges():  # 空图直接返回
        return G

    # 计算每个节点的度数（包含多重边）
    degrees = {u: G.degree(u) for u in G}

    # 收集所有边的未归一化拥挤度
    edges_data = []
    for u, v in G.edges:
        crowdedness = degrees[u] + degrees[v]
        edges_data.append((u, v, crowdedness))

    # 找出最大拥挤度
    max_crowded = max(crowdedness for _, _, crowdedness in edges_data)

    # 遍历所有边并添加归一化属性
    for u, v, crowdedness in edges_data:
        if max_crowded == 0:
            normalized = 0.0
        else:
            normalized = crowdedness / max_crowded
        # 将属性添加到边中，使用字典存储避免键冲突
        nx.set_edge_attributes(G, {(u, v): {'crowdedness': normalized}})


    # 添加时间(只用作测试)
    for u, v, attr in G.edges(data=True):
        vehicle = attr['vehicle']
        distance = attr['distance']
        crowdedness = attr['crowdedness']
        walk_time = float('inf')
        bike_time = float('inf')
        if vehicle == 'walk' or vehicle == 'both':
            real_walk_speed = walk_speed * crowdedness
            # 时间单位为分钟
            walk_time = (distance / 1000) / real_walk_speed * 60
        if vehicle == 'bike' or vehicle == 'both':
            real_bike_speed = bike_speed * crowdedness
            # 时间单位为分钟
            bike_time = (distance / 1000) / real_bike_speed * 60

        nx.set_edge_attributes(G, {(u, v): {
            'walk_time': walk_time, 'bike_time': bike_time, 'time' : min(walk_time, bike_time)
        }})

    return G


def add_prototype_and_type(G):
    '''
    添加建筑物的 原型、类型、显示名
    '''
    if not G.edges():
        return G

    # 路口
    # 计算每个节点的度数（包含多重边）
    degrees = dict(G.degree())

    # 度数降序排序节点，处理相同度数的情况（保持稳定性可加节点本身作为第二关键字）
    sorted_nodes = sorted(degrees.keys(), key=lambda x: (-degrees[x], x))

    for node in sorted_nodes[:20]:
        G.nodes[node]['prototype'] = 'cross'
        G.nodes[node]['type'] = '路口'


    # 其他两种类型
    prototype_distribution = []
    type_building = [x[:-4] for x in os.listdir(r'节点图片\building')]
    type_service = [x[:-4] for x in os.listdir(r'节点图片\service')]
    for j in type_building:
        prototype_distribution.extend([('building',j)]*20)
    for j in type_service:
        prototype_distribution.extend([('service',j)]*5)

    idx=0
    for node in G.nodes:
        if not 'prototype' in G.nodes[node]:
            G.nodes[node]['prototype'] = prototype_distribution[idx][0]
            G.nodes[node]['type'] = prototype_distribution[idx][1]
            idx+=1

    type_list = type_building + type_service + ['路口']


    # 添加名字
    name_count = {k:0 for k in type_list}
    for node in G.nodes:
        type = G.nodes[node]['type']
        name_count[type] +=1
        G.nodes[node]['name'] = f'{type}{name_count[type]}'

    return type_list
