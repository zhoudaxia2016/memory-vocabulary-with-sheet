# 其实不算爬虫
# 需要在浏览器打开视频，点击开启字幕，然后打开浏览器控制台复制字幕请求url
# url作为该脚本第一个参数

import sys
import requests

url = sys.argv[1]
id = sys.argv[2]
res = requests.get(url)
data = [[s['utf8'] for s in _.get('segs') if s.get('acAsrConf') is not None]
  for _ in res.json()['events'] if _.get('segs') is not None]

text = ''
for e in data:
  if len(e) == 0:
    continue
  for s in e:
    text = text + s
  text = text + '\n'

with open('data/' + id, 'w') as f:
  f.write(text)
