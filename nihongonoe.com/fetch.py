# 获取图片
from bs4 import BeautifulSoup

import requests
import json

site = 'https://nihongonoe.com/main-category/person/couple/'
page = requests.get(site)
page.encoding = 'utf-8'
soup = BeautifulSoup(page.text, features="html.parser")
pages = [a.attrs['href'] for a in soup.select('li.page_item a')]
print(len(pages))

allImgs = []
wordSet = set()

i = 0
for p in pages:
  i = i + 1
  print('拉取第{0}个页面，url为{1}'.format(i, p))
  html = requests.get(p)
  soup = BeautifulSoup(html.text, features="html.parser")
  imgs = [[img.attrs['alt'], img.attrs['src']] for img in soup.select('.attachment-thumbnail')]
  for img in imgs:
    if img[0] not in wordSet:
      allImgs.append(img)
      wordSet.add(img[0])

with open('data.json', 'w', encoding='utf8') as json_file:
    json.dump(allImgs, json_file, ensure_ascii=False)
print(len(allImgs))
