from 改造 import *

import matplotlib.image as mpimg
image_path = '北邮.jpg'
image = mpimg.imread(image_path)
shape = image.shape
extent_image = [0, shape[1], 0, shape[0]]


def create_graph_from_files(edges_file, nodes_file):
    G = nx.Graph()
    # 读取节点文件
    with open(nodes_file, 'r', encoding='utf8') as f:
        for line in f:
            node_id, rest = line.strip().split(':')
            x, y, node_type, name = rest.split(',')

            node_id = int(node_id)
            x, y = map(int, [x, y])
            node_type = int(node_type)

            # # 坐标轴修正
            # y = shape[0] - y

            G.add_node(node_id, pos=(x, y), type=node_type, name=name)

    # 读取边文件
    with open(edges_file, 'r') as f:
        for line in f:
            source, target = map(int, line.strip().split(','))
            G.add_edge(source, target, vehicle='walk')

    # 计算边的距离
    def distance(p, q):
        return ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5

    for u, v in G.edges:
        G.edges[(u, v)]['distance'] = distance(G.nodes[u]['pos'], G.nodes[v]['pos'])

    return G

def add_prototype(G):
    '''
    添加建筑物的 原型、类型、显示名
    '''

    type_building = [x[:-4] for x in os.listdir(r'节点图片\building')]
    type_service = [x[:-4] for x in os.listdir(r'节点图片\service')]
    type_cross = [x[:-4] for x in os.listdir(r'节点图片\cross')]
    type_chinese = type_building + type_service + type_cross

    for node in G.nodes:
        node_type_index = G.nodes[node]['type']

        if node_type_index in [0,1,2,3]:
            G.nodes[node]['prototype'] = 'building'
        elif node_type_index in list(range(4,13+1)):
            G.nodes[node]['prototype'] = 'service'
        elif node_type_index == 14:
            G.nodes[node]['prototype'] = 'cross'

        G.nodes[node]['type'] = type_chinese[node_type_index]


# 使用真实数据文件创建图
edges_file = 'edges.txt'
nodes_file = 'nodes.txt'
G = create_graph_from_files(edges_file, nodes_file)

add_crowdedness_to_edges(G)
add_prototype(G)

# print(G.nodes(data=True))
# print(G.edges(data=True))


from graph import *
g = Graph(G.order(), 10)
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



# import matplotlib.pyplot as plt
# # 可视化
# plt.rcParams['font.sans-serif'] = ['SimHei']
#
# fig, ax = plt.subplots(figsize=(shape[1]//100, shape[0]//100))
# ax.set_xlim(0, shape[1])
# ax.set_ylim(0, shape[0])
# plt.xticks(fontsize=36, rotation=45)
# plt.yticks(fontsize=36,)
#
# ax.imshow(image, extent=extent_image, aspect='auto')
# g.visualize_graph(ax)
# plt.show()


import pickle
with open(f'graphMaps\\{'{:06d}'.format(712)}.pickle', 'wb') as f:
    pickle.dump(g, f)
