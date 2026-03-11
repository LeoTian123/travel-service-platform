from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from toolkits.graph import *
import pickle
import os
import json
from typing import Any, Dict, List, Optional, Tuple, Union

from django.conf import settings

from numpy import int32
def convert_int32(data):
    if isinstance(data, int32):
        return int(data)
    elif isinstance(data, dict):
        return {key: convert_int32(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_int32(item) for item in data]
    return data

spot_types = {
    "办公楼": {
        "name": "办公楼",
        "color": "#3F51B5",
        "icon": "🏢"
    },
    "地标": {
        "name": "地标",
        "color": "#FFC107",
        "icon": "🗼"
    },
    "宿舍楼": {
        "name": "宿舍楼",
        "color": "#4CAF50",
        "icon": "🏠"
    },
    "教学楼": {
        "name": "教学楼",
        "color": "#00BCD4",
        "icon": "🏫"
    },
    "体育馆": {
        "name": "体育馆",
        "color": "#F44336",
        "icon": "🏟️"
    },
    "厕所": {
        "name": "厕所",
        "color": "#9E9E9E",
        "icon": "🚾"
    },
    "咖啡": {
        "name": "咖啡",
        "color": "#795548",
        "icon": "☕"
    },
    "商店": {
        "name": "商店",
        "color": "#673AB7",
        "icon": "🛍️"
    },
    "图书馆": {
        "name": "图书馆",
        "color": "#03A9F4",
        "icon": "📚"
    },
    "操场": {
        "name": "操场",
        "color": "#8BC34A",
        "icon": "🏟️"
    },
    "活动中心": {
        "name": "活动中心",
        "color": "#FF9800",
        "icon": "🎭"
    },
    "超市": {
        "name": "超市",
        "color": "#388E3C",
        "icon": "🛒"
    },
    "食堂": {
        "name": "食堂",
        "color": "#FF5722",
        "icon": "🍽️"
    },
    "饭店": {
        "name": "饭店",
        "color": "#FF6347",
        "icon": "🍴"
    },
    "路口": {
        "name": "路口",
        "color": "#FFEB3B",
        "icon": "🚥"
    }
}
path_types = {
    'walk': {
        'color': '#696969',
        'weight': 5,
    },
    'bike': {
        'color': '#A020F0',
        'weight': 5,
    },
    'both': {
        'color': '#4B0082',
        'weight': 10,
    },
}


def list_graph(request):
    graph_id = int(request.GET.get('id', 0))
    file_name = f'{'{:06d}'.format(graph_id)}.pickle'
    with open(os.path.join(settings.BASE_DIR, 'Media\\graphMaps', file_name), 'rb') as f:
        g = pickle.load(f)

    num_nodes = g.num_nodes

    nodes = []
    edges = []
    center_x = 0
    center_y = 0

    for node_id, node_attr in enumerate(g.nodes):
        if node_attr:
            pos = node_attr.pos if node_attr.pos else (0, 0)
            node = {
                'id': int(node_id),  # 确保转换为 int 类型
                'name': node_attr.name if node_attr.name else '未命名',
                'type': node_attr.type if node_attr.type else '未知类型',
                'x': float(pos[0]),
                'y': float(pos[1]),
                'details': {
                    'description': '暂无描述',
                    'image': '暂无图片'
                }
            }
            nodes.append(node)
            center_x += float(pos[0])
            center_y += float(pos[1])

    for from_id, adj_edges in enumerate(g.edges):
        for to_id, edge_attr in adj_edges.items():
            edge = {
                'from': int(from_id),  # 确保转换为 int 类型
                'to': int(to_id),  # 确保转换为 int 类型
                'vehicle': '未知类型' if not edge_attr.vehicle else edge_attr.vehicle,
            }
            edges.append(edge)

    if nodes:
        center_x /= len(nodes)
        center_y /= len(nodes)
    else:
        center_x = 500
        center_y = 500

    boundary = {
        'minX': 0,
        'maxX': 1000,
        'minY': 0,
        'maxY': 1000
    }
    if graph_id == 712:
        boundary = {
            'minX': 0,
            'maxX': 1754,
            'minY': 0,
            'maxY': 1245
        }

    result = {
        'ret': 0,
        'data': {
            'nodes': nodes,
            'edges': edges,
            'center': {
                'x': center_x,
                'y': center_y
            },
            'name': str(graph_id),
            'types': {
                'spotTypes': spot_types,
                'pathTypes': path_types
            },
            'bounds': {
                'virtual': boundary,
                'real': {
                    'minLng': 116.397,
                    'maxLng': 116.405,
                    'minLat': 39.915,
                    'maxLat': 39.920
                }
            }
        }
    }

    return JsonResponse(result)


def best_path_dijkstra(request):
    # weight取值：distance, time, walk_time
    weight: str = request.GET.get('weight')
    start: int = int(request.GET.get('start'))
    end: int = int((request.GET.get('end')))
    graph_id: int = int(request.GET.get('id'))
    file_name = f'{'{:06d}'.format(graph_id)}.pickle'
    with open(os.path.join(settings.BASE_DIR, 'Media\\graphMaps', file_name), 'rb') as f:
        g = pickle.load(f)

    dist, path = g.dijkstra(start, target=end, weight=weight)

    result = {
        'ret': 0,
        'data': {
            'dist': dist,
            'path': path,
        }
    }

    # 转换数据中的 np.int32 类型
    result = convert_int32(result)

    return JsonResponse(result)


def best_path_circuit(request):
    # weight取值：distance, time, walk_time
    weight: str = request.GET.get('weight')

    start: int = int(request.GET.get('start'))

    nodes_str: str = request.GET.get('nodes')
    nodes_list: List[int] = json.loads(nodes_str)

    graph_id: int = int(request.GET.get('id'))
    file_name = f'{'{:06d}'.format(graph_id)}.pickle'
    with open(os.path.join(settings.BASE_DIR, 'Media\\graphMaps', file_name), 'rb') as f:
        g = pickle.load(f)

    path_extracted, path, dist = g.shortest_path_with_visited_nodes(
        start,
        visited_nodes=nodes_list,
        weight=weight
    )

    result = {
        'ret': 0,
        'data': {
            'dist': dist,
            'path': path,
            'path_extracted': path_extracted,
        }
    }

    # 转换数据中的 np.int32 类型
    result = convert_int32(result)

    return JsonResponse(result)


def radar_search(request):
    # weight取值：distance, time, walk_time
    weight: str = request.GET.get('weight')

    start: int = int(request.GET.get('start'))
    k: int = int(request.GET.get('k'))

    node_type: Optional[str] = request.GET.get('node_type', None)

    graph_id: int = int(request.GET.get('id'))
    file_name = f'{'{:06d}'.format(graph_id)}.pickle'
    with open(os.path.join(settings.BASE_DIR, 'Media\\graphMaps', file_name), 'rb') as f:
        g = pickle.load(f)

    result = {
        'ret': 0,
        'data': g.radar_search(start, k, weight, node_type=node_type)
    }

    # 转换数据中的 np.int32 类型
    result = convert_int32(result)

    return JsonResponse(result)