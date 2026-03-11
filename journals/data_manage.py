import pickle
import os
import random
from datetime import datetime, timedelta

# with open('../Media/journals/main-data.pickle', 'rb') as f:
#     data = pickle.load(f)

def get_random_date():
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2024, 1, 1)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')

original_data = [
    {
        "journal_id": 1,
        "title": "故宫一日",
        "date": get_random_date(),
        "spot_id": 1,
        "imgs": [],
        "content": "故宫太震撼了！红墙金瓦特别壮观，走一圈就感受到古代皇家的威严。就是旺季人太多，建议错峰来！",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 2,
        "title": "来爬长城了",
        "date": get_random_date(),
        "spot_id": 2,
        "imgs": [],
        "content": "站在长城上，才能真正体会‘不到长城非好汉’的含义！陡峭的台阶和蜿蜒的城墙让我既震撼又腿软！",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 3,
        "title": "颐和园漫游",
        "date": get_random_date(),
        "spot_id": 3,
        "imgs": [],
        "content": "颐和园的美超乎想象！昆明湖湖水碧波荡漾，十七孔桥宛如长虹卧波。万寿山上佛香阁巍峨耸立，绿树成荫间尽显皇家园林的大气与典雅。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 4,
        "title": "前门大街探秘",
        "date": get_random_date(),
        "spot_id": 4,
        "imgs": [],
        "content": "前门大街古色古香，一砖一瓦都散发着老北京的传统韵味。漫步其中，仿佛穿越回了几十年前，街边的老字号店铺更是让人感受到历史的厚重。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 5,
        "title": "什刹海夜游",
        "date": get_random_date(),
        "spot_id": 5,
        "imgs": [],
        "content": "什刹海真的太有韵味了！古色古香的胡同，波光粼粼的湖水，还有湖边那些文艺的小店，都特别吸引人。夜晚华灯初上，更添一份神秘浪漫。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 6,
        "title": "天安门广场观礼",
        "date": get_random_date(),
        "spot_id": 6,
        "imgs": [],
        "content": "天安门广场真的太震撼了！站在广场上，看着雄伟的天安门城楼，心中的民族自豪感油然而生。升旗仪式更是庄严肃穆，让人心潮澎湃。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 7,
        "title": "故宫深度游",
        "date": get_random_date(),
        "spot_id": 1,
        "imgs": [],
        "content": "故宫不仅建筑宏伟，细节也处处是宝。屋檐上的神兽栩栩如生，护城河倒映着蓝天，随手一拍就是大片。建议租个讲解器，能学到很多历史知识。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 8,
        "title": "长城四季之美",
        "date": get_random_date(),
        "spot_id": 2,
        "imgs": [],
        "content": "秋天来长城最好看！枫叶红得像火，黄叶铺满台阶，站在高处俯瞰群山，感觉整个世界都安静了。不过冬天可能会比较滑，要穿防滑鞋哦。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 9,
        "title": "颐和园晨光",
        "date": get_random_date(),
        "spot_id": 3,
        "imgs": [],
        "content": "清晨的颐和园特别美！薄雾笼罩着昆明湖，远处传来鸟鸣声。沿着西堤散步，看着阳光慢慢照亮十七孔桥，感觉时间都慢下来了。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 10,
        "title": "什刹海酒吧夜",
        "date": get_random_date(),
        "spot_id": 5,
        "imgs": [],
        "content": "晚上来什刹海别有一番风味！湖边酒吧灯光摇曳，驻唱歌手唱着民谣，湖面上倒映着霓虹。不过周末人很多，建议工作日来体验更安静的氛围。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    }
]

# 新增20条数据
new_data = [
    {
        "journal_id": 11,
        "title": "故宫雪景",
        "date": get_random_date(),
        "spot_id": 1,
        "imgs": [],
        "content": "下雪天的故宫美到窒息！红墙白雪交相辉映，仿佛穿越回古代。建议穿防滑鞋，因为石板路很滑。雪后的太和殿特别壮观，拍照一定要带广角镜头！",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 12,
        "title": "长城云海",
        "date": get_random_date(),
        "spot_id": 2,
        "imgs": [],
        "content": "清晨的长城云海太震撼了！站在高处俯瞰，云雾缭绕如同仙境。不过要早点来，太阳出来后云海就散了。建议穿保暖衣物，山顶风很大。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 13,
        "title": "颐和园夏日",
        "date": get_random_date(),
        "spot_id": 3,
        "imgs": [],
        "content": "夏天的颐和园特别美！荷花盛开，湖面上游船点点。傍晚时分在长廊散步，看夕阳西下，感受皇家园林的宁静与优雅。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 14,
        "title": "前门小吃",
        "date": get_random_date(),
        "spot_id": 4,
        "imgs": [],
        "content": "前门大街的小吃太丰富了！炸酱面、卤煮、糖葫芦...每样都想尝。不过有些店铺排队很长，建议错峰用餐。老字号的味道确实正宗。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 15,
        "title": "什刹海滑冰",
        "date": get_random_date(),
        "spot_id": 5,
        "imgs": [],
        "content": "冬天的什刹海可以滑冰！租个冰车或者冰鞋，在冰面上畅快滑行。不过要注意安全，初学者建议找教练指导。湖边的糖葫芦特别甜！",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 16,
        "title": "国庆天安门",
        "date": get_random_date(),
        "spot_id": 6,
        "imgs": [],
        "content": "国庆节的天安门广场人山人海！花坛布置得特别漂亮，五星红旗迎风飘扬。虽然人多，但能感受到浓厚的节日氛围，很值得来。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 17,
        "title": "故宫珍宝馆",
        "date": get_random_date(),
        "spot_id": 1,
        "imgs": [],
        "content": "故宫珍宝馆值得一看！各种金银珠宝、玉器瓷器让人目不暇接。建议提前预约，因为限流。里面的展品都是无价之宝，能近距离欣赏太幸运了。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 18,
        "title": "长城夜游",
        "date": get_random_date(),
        "spot_id": 2,
        "imgs": [],
        "content": "八达岭长城夜游太特别了！灯光照亮古老的城墙，仿佛穿越回古代。不过晚上比较冷，建议多穿衣服。夜游的人不多，可以慢慢欣赏。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 19,
        "title": "颐和园游船",
        "date": get_random_date(),
        "spot_id": 3,
        "imgs": [],
        "content": "在颐和园租船游湖很惬意！可以选择脚踏船或者电动船。划到昆明湖中央，欣赏四周的风景，感受皇家园林的宁静与美丽。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 20,
        "title": "前门老字号",
        "date": get_random_date(),
        "spot_id": 4,
        "imgs": [],
        "content": "前门大街的老字号店铺值得一逛！瑞蚨祥的绸缎、张一元的茶叶、内联升的布鞋...每一家都有百年历史，能买到地道的北京特产。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 21,
        "title": "什刹海胡同",
        "date": get_random_date(),
        "spot_id": 5,
        "imgs": [],
        "content": "什刹海的胡同很有老北京特色！可以骑着共享单车穿梭其中，感受老北京的市井生活。有些四合院可以参观，了解传统的北京居住文化。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 22,
        "title": "天安门升旗",
        "date": get_random_date(),
        "spot_id": 6,
        "imgs": [],
        "content": "凌晨来看天安门升旗仪式太震撼了！当国旗伴随国歌缓缓升起，全场肃立，爱国情怀油然而生。建议提前两小时到，找个好位置。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 23,
        "title": "故宫角楼",
        "date": get_random_date(),
        "spot_id": 1,
        "imgs": [],
        "content": "故宫的角楼太美了！无论是晴天还是雪天，都有不同的韵味。建议从护城河边拍摄，能拍到角楼倒映在水中的美景，特别适合摄影爱好者。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 24,
        "title": "长城好汉坡",
        "date": get_random_date(),
        "spot_id": 2,
        "imgs": [],
        "content": "终于爬到了长城的好汉坡！虽然过程很累，但站在高处俯瞰群山，感觉一切都值得。建议穿舒适的运动鞋，带足够的水和食物。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 25,
        "title": "颐和园佛香阁",
        "date": get_random_date(),
        "spot_id": 3,
        "imgs": [],
        "content": "颐和园的佛香阁是必打卡点！登上高处可以俯瞰整个昆明湖和万寿山。里面的佛像庄严肃穆，建筑细节精美，体现了古代工匠的高超技艺。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 26,
        "title": "前门全聚德",
        "date": get_random_date(),
        "spot_id": 4,
        "imgs": [],
        "content": "在前门大街的全聚德吃烤鸭太正宗了！鸭皮酥脆，鸭肉鲜嫩，配上薄饼、葱丝和甜面酱，简直是人间美味。就是价格有点小贵，但值得尝试。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 27,
        "title": "什刹海日落",
        "date": get_random_date(),
        "spot_id": 5,
        "imgs": [],
        "content": "什刹海的日落特别美！看着太阳慢慢沉入湖面，整个天空被染成橙红色。建议带上相机，捕捉这美丽的瞬间。湖边的咖啡馆可以边喝咖啡边欣赏美景。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 28,
        "title": "天安门广场夜景",
        "date": get_random_date(),
        "spot_id": 6,
        "imgs": [],
        "content": "天安门广场的夜景太壮观了！灯光照亮整个广场，人民英雄纪念碑和毛主席纪念堂在灯光下显得格外庄严。广场上还有很多市民跳广场舞，充满生活气息。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 29,
        "title": "故宫珍禽异兽",
        "date": get_random_date(),
        "spot_id": 1,
        "imgs": [],
        "content": "故宫屋檐上的神兽太有趣了！每一只都栩栩如生，形态各异。导游说它们有不同的寓意，比如龙代表皇权，狮子象征守护。仔细观察能发现很多细节。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 30,
        "title": "长城烽火台",
        "date": get_random_date(),
        "spot_id": 2,
        "imgs": [],
        "content": "长城上的烽火台保存得很完好！站在上面可以远眺群山，想象古代士兵传递军情的样子。有些烽火台内部还能参观，了解古代的防御体系。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 31,
        "title": "颐和园西堤",
        "date": get_random_date(),
        "spot_id": 3,
        "imgs": [],
        "content": "颐和园的西堤像江南水乡！垂柳依依，桃花盛开，湖面上有小船划过。沿着西堤漫步，感受皇家园林的精致与优雅，是拍照的好地方。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 32,
        "title": "前门瑞蚨祥",
        "date": get_random_date(),
        "spot_id": 4,
        "imgs": [],
        "content": "在前门大街的瑞蚨祥买绸缎太赞了！店员服务态度很好，可以根据需求推荐合适的布料。这里还有很多传统的中式服装和配饰，适合买伴手礼。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 33,
        "title": "什刹海冰场",
        "date": get_random_date(),
        "spot_id": 5,
        "imgs": [],
        "content": "冬天的什刹海冰场特别热闹！可以滑冰车、打冰球，还能看到民间艺人表演。租个冰鞋自己滑也很有趣，不过要注意安全，初学者建议找教练。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 34,
        "title": "天安门广场升旗仪式",
        "date": get_random_date(),
        "spot_id": 6,
        "imgs": [],
        "content": "凌晨来看天安门升旗仪式太震撼了！当国旗伴随国歌缓缓升起，全场肃立，爱国情怀油然而生。建议提前两小时到，找个好位置。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },
    {
        "journal_id": 35,
        "title": "故宫九龙壁",
        "date": get_random_date(),
        "spot_id": 1,
        "imgs": [],
        "content": "故宫的九龙壁太精美了！九条龙形态各异，栩栩如生，仿佛随时会腾空而起。壁上的琉璃色彩鲜艳，历经百年依然光彩夺目，是拍照的好背景。",
        "user_id": random.randint(1, 10),
        "num_likes": 0
    },]

data = original_data + new_data
print(data)
print(len(data))

for i in range(6):
    data[i]['imgs'].append(f'img{2*i}.jpg')
    data[i]['imgs'].append(f'img{2*i+1}.jpg')
for i in range(10,17):
    data[i]['imgs'].append(f'img{2*i}.jpg')
    data[i]['imgs'].append(f'img{2*i+1}.jpg')

with open('../Media/journals/main-data.pickle', 'wb') as f:
    pickle.dump(data, f)


# import requests

# for i in range(100):
#     print(i)
#     url = 'https://picsum.photos/800/600?random=2'
#     r = requests.get(url)
#     with open(f'../Media/journals/img/img{i}.jpg', 'wb') as f:
#         f.write(r.content)