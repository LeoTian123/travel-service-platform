from graph import *
from 改造 import *
import matplotlib.pyplot as plt


# 示例使用
np.random.seed(42)
random.seed(42)
G = generate_graph()
add_crowdedness_to_edges(G)
add_prototype_and_type(G)

# print(G.edges(data=True))
# print(G.nodes(data=True))

g = Graph(G.order(), bike_speed)
for node,attr in G.nodes(data=True):
    pos = attr['pos']
    prototype = attr['prototype']
    node_type = attr['type']
    name = attr['name']
    g.add_node(node,pos,prototype,node_type,name)

for u,v,attr in G.edges(data=True):
    vehicle = attr['vehicle']
    distance = attr['distance']
    crowdedness = attr['crowdedness']
    # walk_time = attr['walk_time']
    # bike_time = attr['bike_time']
    g.add_edge(u,v,vehicle,distance,crowdedness)

print(g)

# print(G[145][148])
# print(g.get_edge_attributes(145,148))
dist, path = g.dijkstra(58, target=69, weight='time')
print(dist, path)
# (length, path) = nx.single_source_dijkstra(G, 58, target=69, weight='time')
# print(length, path)

start, nodes = 8, [137,24,26,132,144,53]
best_path, best_path_extended, min_time = g.shortest_path_with_visited_nodes(start, nodes, 'bike_time')
print("最短路径:", best_path)
print("最短拓扑路径:", best_path_extended)
print("总时间:", min_time)

print(g.radar_search(146, 20,'distance'))
print(g.radar_search(146, 20,'distance','厕所'))

size = 0
for i in g.adjacency_list:
    for j in i:
        size+=1
print(size)

# # 可视化
# plt.rcParams['font.sans-serif'] = ['SimHei']
# plt.figure()
#
# fig, ax = plt.subplots(figsize=(25, 25))
# ax.set_xlim(-50, 1050)
# ax.set_ylim(-50, 1050)
# plt.xticks(fontsize=36, rotation=45)
# plt.yticks(fontsize=36,)
# g.visualize_graph(ax)
# plt.show()
#
# plt.close()  # 显式关闭释放内存
# plt.figure()
#
# fig, ax = plt.subplots(figsize=(25, 25))
# ax.set_xlim(-50, 1050)
# ax.set_ylim(-50, 1050)
# plt.xticks(fontsize=36, rotation=45)
# plt.yticks(fontsize=36,)
# g.visualize_graph(ax, best_path_extended, 'bike_time')
# plt.show()
