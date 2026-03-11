import pickle
import os

# 这个文件直接操作生的python数据，操作级别要比AttractionsManager提供的测试函数还要高

with open('../Media/attractions/main-data.pickle', 'rb') as f:
    data = pickle.load(f)

'''2025.03.31晚'''
# 删除了if_mapped字段 因为到时候所有的景点都有地图
# for i in data:
#     del i['if_mapped']

'''2025.04.06晚'''
# 故宫图片错误
# data[0]['img_url'] = 'https://img1.qunarzz.com/travel/d9/1803/c1/46a6398c92f17fb5.jpg_r_480x360x95_d05b4420.jpg'

'''2025.04.14晚'''
# 北邮图片错误
# data[-1]['img_url'] = 'http://10.129.229.111:8081/Media/北邮校徽.jpg'

'''2025.04.24上午'''
# 增加num_journals字段 删除喜欢字段
# for i in data:
#     i['num_journals'] = 0
#     if 'is_liked' in i:
#         del i['is_liked']

print(data)
print(len(data))

# with open('../Media/attractions/main-data.pickle', 'wb') as f:
#     pickle.dump(data, f)