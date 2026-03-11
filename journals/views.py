from copy import deepcopy

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

import pickle
import os
import json
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User

from django.views.decorators.cache import cache_control
from toolkits.ImageCompressor import ImageCompressor

# 初始化 LikeTable
from toolkits.LikeTable import LikeTable
like_table = LikeTable(os.path.join(settings.BASE_DIR, 'Media/journals/like_table.pickle'))

# 初始化 JournalsManager
from .journals_manager import JournalsManager
journals_manager = JournalsManager(
    os.path.join(settings.BASE_DIR, 'Media/journals', 'main-data.pickle')
)

# 初始化景点id到其他信息的哈希表/字典
from attractions.attractions_manager import AttractionsManager
attractions_manager = AttractionsManager(
    os.path.join(settings.BASE_DIR, 'Media/attractions/main-data.pickle')
)
# 初始化景点id到name的字典
attraction_id_to_name = {}
for attraction in attractions_manager.get_attractions():
    attraction_id_to_name[attraction['id']] = attraction['cnName']

# 初始化景点id到index的字典
attraction_id_to_idx = {}
for idx, attraction in enumerate(attractions_manager.get_attractions()):
    attraction_id_to_idx[attraction['id']] = idx


def list_journals(request):
    """
    获取日记列表接口
    方法: GET

    查询参数:
        page_num (int): 当前页码，默认为 0
        page_size (int): 每页数量，默认为 30
        keyword (str): 关键词筛选，用于搜索日记标题或内容
        spot_id (str): 可选，景点 ID 筛选参数
        uploader_id (str): 可选，上传者 ID 筛选参数
        sort_type (str): 排序类型（如 'likes' 表示按点赞数排序）
        sort_direction (str): 排序方向（'asc' 表示升序，'desc' 表示降序）
        user_id (int): 当前用户 ID，用于判断是否点赞等操作

    响应:
        成功:
            {
                "ret": 0,
                "data": {
                    "length": <int>,  # 当前页数据数量
                    "retlist": <list>,  # 日记列表，每个日记包含以下信息：
                        - 'spot_name': 景点名称
                        - 'img_cover': 日记的封面图片（取第一张图片）
                        - 'user_name': 上传者的用户名
                        - 'is_liked': 当前用户是否点赞该日记
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
    spot_id = request.GET.get('spot_id')  # 获取景点ID筛选参数
    uploader_id = request.GET.get('uploader_id')  # 获取上传者ID筛选参数
    sort_type = request.GET.get('sort_type', '')
    sort_direction = request.GET.get('sort_direction', '')

    # 获取用户id
    user_id = int(request.GET.get('user_id', 0))

    journals_data = journals_manager.get_journals_paginated(
        keyword=keyword,
        spot_id=spot_id,
        uploader_id=uploader_id,
        sort_type=sort_type,
        sort_direction=sort_direction,
        page_num=page_num,
        page_size=page_size
    )

    # 获取当前页数据
    retlist = journals_data['data']

    # 修磨一下，这段实际上已经做了解耦，因为这个工作本就不应该封装，是一个接口工作
    for jou in retlist:
        # spot_name
        jou['spot_name'] = attraction_id_to_name[jou['spot_id']]
        # del jou['spot_id']

        # img_cover
        if jou['imgs']:
            jou['img_cover'] = jou['imgs'][0]
        else:
            jou['img_cover'] = None
        # del jou['imgs']

        # user_name
        user = User.objects.get(id=jou['user_id'])
        jou['user_name'] = user.username
        # del jou['user_id']

        # is_liked
        jou['is_liked'] = like_table.has_liked(user_id=user_id, post_id=jou['journal_id'])

    return JsonResponse({
        'ret': 0,
        'data': {
            'length': journals_data['length'],
            'retlist': retlist,
            'current_page': journals_data['current_page'],
            'page_size': journals_data['page_size'],
            'total_pages': journals_data['total_pages']
        }
    })



def like_journals(request):
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
        post_id = data.get('journal_id')

        if user_id is None or post_id is None:
            return JsonResponse({'error': '缺少 user_id 或 journal_id'}, status=400)

        user_id = int(user_id)
        post_id = int(post_id)

        if like_table.like(user_id, post_id):

            # 更新数据集的点赞数
            journals_manager.like_journal(post_id)

            return JsonResponse({
                'status': 'success',
                'action': 'liked',
                'likes_count': journals_manager.get_journals()[post_id-1]['num_likes']
            })
        else:
            return JsonResponse({
                'status': 'success',
                'action': 'already_liked',
                'likes_count': journals_manager.get_journals()[post_id-1]['num_likes']
            })

    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的 JSON 数据'}, status=400)
    except ValueError:
        return JsonResponse({'error': 'user_id 和 post_id 必须是整数'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def unlike_journals(request):
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
        post_id = data.get('journal_id')

        if user_id is None or post_id is None:
            return JsonResponse({'error': '缺少 user_id 或 journal_id'}, status=400)

        user_id = int(user_id)
        post_id = int(post_id)

        if like_table.unlike(user_id, post_id):

            # 更新数据集的点赞数
            journals_manager.unlike_journal(post_id)

            return JsonResponse({
                'status': 'success',
                'action': 'unliked',
                'likes_count': journals_manager.get_journals()[post_id-1]['num_likes']
            })
        else:
            # 用户未点赞或发生其他错误
            return JsonResponse({
                'status': 'success',
                'action': 'not_liked',  # 用户未点赞
                'likes_count': journals_manager.get_journals()[post_id-1]['num_likes']
            })

    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的 JSON 数据'}, status=400)
    except Exception as e:
        # 捕获其他可能的异常，如文件IO错误等
        return JsonResponse({'error': str(e)}, status=500)


def list_journals_detail(request):
    """
        获取日志详情接口

        请求方式: GET
        请求参数:
            journal_id (int, 必填): 日志ID，从1开始计数
            user_id (int, 可选): 用户ID，用于判断是否点赞

        返回数据:
            {
                "ret": 0,  # 状态码，0表示成功，非0表示失败
                "journal": {  # 日志详情
                    "journal_id": int,  # 日志ID
                    "title": str,  # 日志标题
                    "date": str,  # 日期，格式YYYY-MM-DD
                    "spot_id": int,  # 景点ID
                    "spot_name": str,  # 景点名称（通过spot_id转换）
                    "imgs": list[str],  # 图片列表
                    "img_cover": str or None,  # 封面图片（取imgs第一张），无图片时为None
                    "content": str,  # 日志内容
                    "user_id": int,  # 用户ID
                    "user_name": str,  # 用户名
                    "num_likes": int,  # 点赞总数
                    "is_liked": bool  # 当前用户是否已点赞
                }
            }
    """
    if request.method != 'GET':
        return JsonResponse({'ret': 1, 'message': '仅支持 GET 请求'}, status=405)

    # 获取journal_id
    journal_id = int(request.GET.get('journal_id', 0))

    # 获取用户id
    user_id = int(request.GET.get('user_id'), 0)

    # 读取数据 是一个面向过程的写法 暂时如此
    jou = journals_manager.get_journals()[journal_id-1]
    jou = deepcopy(jou)

    # 修磨
    # spot_name
    jou['spot_name'] = attraction_id_to_name[jou['spot_id']]

    # img_cover
    if jou['imgs']:
        jou['img_cover'] = jou['imgs'][0]
    else:
        jou['img_cover'] = None

    # user_name
    user = User.objects.get(id=jou['user_id'])
    jou['user_name'] = user.username

    # is_liked
    jou['is_liked'] = like_table.has_liked(user_id=user_id, post_id=jou['journal_id'])


    return JsonResponse({
        'ret': 0,
        'journal': jou
    })


def list_journals_user(request):

    if request.method != 'GET':
        return JsonResponse({'ret': 1, 'message': '仅支持 GET 请求'}, status=405)

    # 获取分页参数
    page_num = int(request.GET.get('page_num', 0))
    page_size = int(request.GET.get('page_size', 30))

    # 获取用户id
    user_id = int(request.GET.get('user_id'))

    # 使用 JournalsManager 获取用户已点赞的景点数据
    user_liked_attractions = journals_manager.get_user_liked_journals(user_id=user_id, like_table=like_table)

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

    # 修磨一下
    username = User.objects.get(id=user_id).username
    for jou in retlist:
        # spot_name
        jou['spot_name'] = attraction_id_to_name[jou['spot_id']]
        # del jou['spot_id']

        # img_cover
        if jou['imgs']:
            jou['img_cover'] = jou['imgs'][0]
        else:
            jou['img_cover'] = None
        # del jou['imgs']

        # user_name
        jou['user_name'] = username
        # del jou['user_id']

        # is_liked
        jou['is_liked'] = True


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


def list_attraction_id_and_name(request):
    return JsonResponse({
        'ret': 0,
        'data': list(attraction_id_to_name.items())
    })


def create_journal(request):
    try:
        # 获取表单数据
        title = request.POST.get('title')
        date = request.POST.get('date')
        spot_id = int(request.POST.get('spot_id'))
        content = request.POST.get('content')
        user_id = int(request.POST.get('user_id'))

        # 获取图片文件
        imgs = request.FILES.getlist('imgs')

        # 图片目录相关
        img_base_path = os.path.join(settings.BASE_DIR, 'Media/journals/img')
        os.makedirs(img_base_path, exist_ok=True)

        # 使用数据管理类添加日记
        new_journal = journals_manager.add_journal(
            title=title,
            date=date,
            spot_id=spot_id,
            content=content,
            user_id=user_id,
            imgs=imgs,
            base_img_path=img_base_path
        )

        # 这些是已保存的文件名
        processed_imgs = new_journal['imgs']

        journal_data = {
            'title': title,
            'date': date,
            'spot_id': spot_id,
            'content': content,
            'user_id': user_id,
            'imgs': processed_imgs  # 返回处理后的文件名
        }

        # 修改attractions_manager的数据
        spot_index = attraction_id_to_idx[journal_data['spot_id']]
        attractions_manager._data[spot_index]['num_journals'] += 1
        attractions_manager._save_data()

        return JsonResponse({"ret": 0, "data": journal_data})
    except Exception as e:
        return JsonResponse({"ret": 1, "msg": str(e)})


@cache_control(max_age=3600)
def get_journal_image(request, filename):
    """获取日记图片，支持压缩图片的解压缩"""
    try:
        # 构建图片基础路径
        base_img_path = os.path.join(settings.BASE_DIR, 'Media/journals/img')

        img_path = os.path.join(base_img_path, filename)
        if os.path.exists(img_path):
            # 确定内容类型
            if filename.lower().endswith('.png'):
                content_type = 'image/png'
            elif filename.lower().endswith(('.jpg', '.jpeg')):
                content_type = 'image/jpeg'
            else:
                return HttpResponse("Unsupported image format", status=400)

            # 直接返回原始图片
            with open(img_path, 'rb') as f:
                return HttpResponse(f.read(), content_type=content_type)

        # 如果都不存在，返回404
        return HttpResponse("Image not found", status=404)

    except Exception as e:
        return HttpResponse(f"Error retrieving image: {str(e)}", status=500)
