import requests
from bs4 import BeautifulSoup
# 定义一个函数，用于抓取和保存单页数据
url = f'https://travel.qunar.com/p-cs299914-beijing-jingdian-3-1'

my_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.64"
}

res = requests.get(url, headers=my_headers)
soup = BeautifulSoup(res.text, features="html.parser")
tag_list = soup.find_all(name="li", attrs={"class": "item"})

print(tag_list)
for tag in tag_list[5:]:

    # 提取中文名字和英文名字
    cn_tit = tag.find('span', class_='cn_tit')
    en_tit = tag.find('span', class_='en_tit')

    # 提取图片链接
    img_link = tag.find('img', class_='img')

    # 提取描述
    description = tag.find('div', class_='desbox')

    # 提取点评数量
    comment_count = tag.find('div', class_='comment_sum')

    cnName = cn_tit.text
    enName = en_tit.text
    cnName = cnName[:-len(enName)]
    print(f"中文名字: {cnName}")
    print(f"英文名字: {enName}")
    print(f"图片链接: {img_link.get('src')}")
    print(f"描述: {description.text}")
    print(f"点评数量: {comment_count.text}")
    print()

