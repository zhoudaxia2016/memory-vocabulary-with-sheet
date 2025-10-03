import requests
from bs4 import BeautifulSoup
import re

level = 5
total_words = []

def get_url(l, p):
  url = 'https://jlptsensei.com/jlpt-n' + str(l) + '-vocabulary-list/' # 替换成你想爬取的网址
  if p != 1:
    url = url + 'page/' + str(p) + '/'
  return url

while True:
  if level < 1:
    break
  p = 1
  while True:
    print('Get level: ', level)
    url = get_url(level, p)
    print('request: ', url)
    response = requests.get(url)

    if response.status_code == 200:
      soup = BeautifulSoup(response.text, 'html.parser')
      kanas = soup.select('tbody :not(.jp).jl-link')
      kanas = [w.get_text() for w in kanas]
      words = soup.select('tbody .jp')
      words = [w.get_text() for w in words]
      for i, w in enumerate(words):
        match = re.search(r'([\u3040-\u309f]+)', kanas[i])
        word = [w, match and match.group(1) or '', str(level)]
        total_words.append(','.join(word))
    else:
      print(f"请求失败，状态码: {response.status_code}")
      break
    p = p + 1
  level = level - 1

with open('words.txt', 'w', encoding='utf-8') as f:
  f.writelines('\n'.join(total_words))
