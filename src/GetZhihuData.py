from bs4 import BeautifulSoup
import requests
import re
import sys

# %%
# https://github.com/egrcc/zhihu-python

headers = {
    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
    'Host': "www.zhihu.com",
    'Origin': "http://www.zhihu.com",
    'Pragma': "no-cache",
    'Referer': "http://www.zhihu.com/"
}

url = 'https://www.zhihu.com/people/guofei9987'

r = requests.get(url, headers=headers, verify=False)
soup = BeautifulSoup(r.content, "lxml")

# %%获取
stars = soup.find_all(name='div', attrs={'class': 'css-1jf3292'})
print(stars[0].text)  # 点赞、喜欢、收藏

# 关注者数量
follows = soup.find_all(name='strong', attrs={'class': 'NumberBoard-itemValue'})
print(follows[1].text)  # 关注
follows_num = follows[1].text

agree, like, collection = re.findall('[0-9,]+', stars[0].text)
# agree, collection = re.findall('[0-9,]+', stars[0].text)


# %%写入到json
import json

achievement = dict()

achievement['zhihu_agree'] = agree
achievement['zhihu_like'] = like
achievement['zhihu_collection'] = collection
achievement['zhihu_follows'] = follows_num


# 把数字变成 '20k' 这种格式
def num2k(x):
    return str(round(int(x.replace(',', '')) / 1000)) + 'k'


achievement['zhihu_agree_str'] = num2k(agree)
achievement['zhihu_like_str'] = num2k(like)
achievement['zhihu_collection_str'] = num2k(collection)
achievement['zhihu_follows_str'] = follows_num  # num2k(follows[1].text)

with open('achievement.json', 'w') as f:
    json.dump(achievement, f, ensure_ascii=False, indent='')
