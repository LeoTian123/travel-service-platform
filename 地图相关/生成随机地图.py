from graph import *
from 改造 import *
import pickle

with open('main-data.pickle', 'rb') as f:
    data = pickle.load(f)

print(data[0])
for each in data:
    # if each['id']!=1:
    #     continue
    G = generate_graph()
    add_crowdedness_to_edges(G)
    add_prototype_and_type(G)

    if each['type']=='景区':
        g = Graph(G.order(), 15)
    else:
        g = Graph(G.order(), 10)
    for node, attr in G.nodes(data=True):
        pos = attr['pos']
        prototype = attr['prototype']
        node_type = attr['type']
        name = attr['name']
        g.add_node(node, pos, prototype, node_type, name)

    for u, v, attr in G.edges(data=True):
        vehicle = attr['vehicle']
        distance = attr['distance']
        crowdedness = attr['crowdedness']
        g.add_edge(u, v, vehicle, distance, crowdedness)

    with open(f'graphMaps\\{'{:06d}'.format(each['id'])}.pickle', 'wb') as f:
        pickle.dump(g, f)