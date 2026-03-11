from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

import os
from django.conf import settings
import json

# 初始化 LikeTable
from toolkits.LikeTable import *
like_table = LikeTable(os.path.join(settings.BASE_DIR, 'Media/attractions/like_table.pickle'))

# 初始化 AttractionsManager
from .attractions_manager import AttractionsManager
attractions_manager = AttractionsManager(
    os.path.join(settings.BASE_DIR, 'Media/attractions/main-data.pickle')
)

# 初始化景点id到index的字典
attraction_id_to_idx = {}
for idx, attraction in enumerate(attractions_manager.get_attractions()):
    attraction_id_to_idx[attraction['id']] = idx


def list_attractions(request):
    """
    获取景点列表接口
    方法: GET
    查询参数:
        page_num (int): 当前页码，默认为0
        page_size (int): 每页数量，默认为30
        keyword (str): 关键词筛选
        type (str): 景点类型筛选
        sort_type (str): 排序类型（如 'comments', 'likes'）
        sort_direction (str): 排序方向（'asc' 或 'rev'）
        user_id (int): 当前用户的ID
    响应:
        成功:
            {
                "ret": 0,
                "data": {
                    "length": <int>,  # 当前页数据数量
                    "retlist": <list>,  # 景点列表
                    "current_page": <int>,  # 当前页码
                    "page_size": <int>,  # 每页数量
                    "total_pages": <int>  # 总页数
                }
            }
        失败:
            {
                "ret": 1,
                "message": "<错误信息>"
            }
    """
    if request.method != 'GET':
        return JsonResponse({'ret': 1, 'message': '仅支持 GET 请求'}, status=405)

    # 获取分页参数
    page_num = int(request.GET.get('page_num', 0))
    page_size = int(request.GET.get('page_size', 30))

    # 获取筛选和排序参数
    keyword = request.GET.get('keyword', '')
    spot_type = request.GET.get('type', '')
    sort_type = request.GET.get('sort_type', '')
    sort_direction = request.GET.get('sort_direction', '')

    # 获取用户id
    user_id = int(request.GET.get('user_id', 0))

    # 使用 AttractionsManager 获取筛选、搜索、分页后的景点数据
    attractions_data = attractions_manager.get_attractions_paginated(
        keyword=keyword,
        spot_type=spot_type,
        sort_type=sort_type,
        sort_direction=sort_direction,
        page_num=page_num,
        page_size=page_size
    )

    retlist = attractions_data['data']
    # 修磨一下，为每个景点添加 'isLiked' 键
    for spot in retlist:
        spot_id = spot.get('id')
        if spot_id is None:
            spot['is_liked'] = False
            continue
        spot['is_liked'] = like_table.has_liked(user_id=user_id, post_id=spot_id)

    return JsonResponse({
        'ret': 0,
        'data': {
            'length': len(retlist),
            'retlist': retlist,
            'current_page': page_num,
            'page_size': page_size,
            'total_pages': attractions_data['total_pages']
        }
    })


def like_attractions(request):
    """
    点赞接口
    方法: POST
    请求体:
        {
            "user_id": <int>,  # 用户ID
            "post_id": <int>   # 帖子ID
        }
    响应:
        成功:
            {
                "status": "success",
                "action": "liked",  # 表示点赞成功
                "likes_count": <int>  # 当前帖子的总点赞数
            }
        失败:
            {
                "error": "<错误信息>"
            }
    """
    if request.method != 'POST':
        return JsonResponse({'error': '仅支持 POST 请求'}, status=405)

    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        post_id = data.get('post_id')

        if user_id is None or post_id is None:
            return JsonResponse({'error': '缺少 user_id 或 post_id'}, status=400)

        user_id = int(user_id)
        post_id = int(post_id)

        if like_table.like(user_id, post_id):

            # 更新数据集的点赞数
            attractions_manager.like_attraction(post_id)

            return JsonResponse({
                'status': 'success',
                'action': 'liked',
                'likes_count': attractions_manager.get_attractions()[attraction_id_to_idx[post_id]]['num_likes']
            })
        else:
            return JsonResponse({
                'status': 'success',
                'action': 'already_liked',
                'likes_count': attractions_manager.get_attractions()[attraction_id_to_idx[post_id]]['num_likes']
            })

    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的 JSON 数据'}, status=400)
    except ValueError:
        return JsonResponse({'error': 'user_id 和 post_id 必须是整数'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def unlike_attractions(request):
    """
    取消点赞接口
    方法: POST
    请求体:
        {
            "user_id": <int>,
            "post_id": <int>
        }
    响应:
        成功:
            {
                "status": "success",
                "action": "unliked",
                "likes_count": <int>  # 取消点赞后的点赞数
            }
        失败:
            {
                "error": "<错误信息>"
            }
    """
    if request.method != 'POST':
        return JsonResponse({'error': '仅支持 POST 请求'}, status=405)

    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        post_id = data.get('post_id')

        if user_id is None or post_id is None:
            return JsonResponse({'error': '缺少 user_id 或 post_id'}, status=400)

        try:
            user_id = int(user_id)
            post_id = int(post_id)
        except ValueError:
            return JsonResponse({'error': 'user_id 和 post_id 必须是整数'}, status=400)

        if like_table.unlike(user_id, post_id):

            # 更新数据集的点赞数
            attractions_manager.unlike_attraction(post_id)

            return JsonResponse({
                'status': 'success',
                'action': 'unliked',
                'likes_count': attractions_manager.get_attractions()[attraction_id_to_idx[post_id]]['num_likes']
            })
        else:
            # 用户未点赞或发生其他错误
            return JsonResponse({
                'status': 'success',
                'action': 'not_liked',  # 用户未点赞
                'likes_count': attractions_manager.get_attractions()[attraction_id_to_idx[post_id]]['num_likes']
            })

    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的 JSON 数据'}, status=400)
    except Exception as e:
        # 捕获其他可能的异常，如文件IO错误等
        return JsonResponse({'error': str(e)}, status=500)


def list_attractions_user(request):

    if request.method != 'GET':
        return JsonResponse({'ret': 1, 'message': '仅支持 GET 请求'}, status=405)

    # 获取分页参数
    page_num = int(request.GET.get('page_num', 0))
    page_size = int(request.GET.get('page_size', 30))

    # 获取用户id
    user_id = int(request.GET.get('user_id'))

    # 使用 AttractionsManager 获取用户已点赞的景点数据
    user_liked_attractions = attractions_manager.get_user_liked_attractions(user_id=user_id, like_table=like_table)

    # 计算分页
    total_num = len(user_liked_attractions)
    index_left = page_size * page_num
    index_right = page_size * (page_num + 1)

    if index_right > total_num:
        index_right = total_num
    if index_left >= total_num:
        return JsonResponse({
            'ret': 0,
            'data': {
                'length': 0,
                'retlist': [],
                'current_page': page_num,
                'page_size': page_size,
                'total_pages': 0
            }
        })

    # 获取当前页数据
    retlist = user_liked_attractions[index_left:index_right]

    # 为每个景点添加 'isLiked' 键
    for spot in retlist:
        spot['is_liked'] = True

    return JsonResponse({
        'ret': 0,
        'data': {
            'length': len(retlist),
            'retlist': retlist,
            'current_page': page_num,
            'page_size': page_size,
            'total_pages': (total_num + page_size - 1) // page_size
        }
    })


def get_UBCF(request):
    """
    获取基于用户协同过滤的景点推荐
    方法: GET
    查询参数:
        user_id (int): 当前用户的ID
        count (int): 需要的推荐数量，默认为10
    响应:
        成功:
            {
                "ret": 0,
                "data": {
                    "recommendations": <list>  # 推荐的景点列表
                }
            }
        失败:
            {
                "ret": 1,
                "message": "<错误信息>"
            }
    """
    if request.method != 'GET':
        return JsonResponse({'ret': 1, 'message': '仅支持 GET 请求'}, status=405)

    # 获取用户ID和推荐数量
    user_id = int(request.GET.get('user_id', 0))
    count = int(request.GET.get('count', 10))

    if user_id <= 0:
        return JsonResponse({'ret': 1, 'message': '用户ID无效'}, status=400)

    try:
        # 获取推荐景点列表
        recommended_attractions = attractions_manager.get_UBCF(
            like_table,
            user_id,
            count
        )

        # 为每个景点添加is_liked信息
        for attraction in recommended_attractions:
            attraction['is_liked'] = like_table.has_liked(user_id, attraction['id'])

        return JsonResponse({
            'ret': 0,
            'data': {
                'recommendations': recommended_attractions
            }
        })
    except Exception as e:
        return JsonResponse({'ret': 1, 'message': f'获取推荐失败: {str(e)}'}, status=500)
