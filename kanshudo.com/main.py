import requests
import csv
from bs4 import BeautifulSoup, element
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

words = []

def getPage(level, offset):
  url = f'https://www.kanshudo.com/collections/wikipedia_jlpt/WPJLPT-N{level}-{offset}'
  page = requests.get(url, headers=headers)
  soup = BeautifulSoup(page.text, features="html.parser")
  wordEles = soup.select('.jukugo a')
  for _ in wordEles:
    word = ''
    kana = ''
    for child in _.descendants:
      if type(child) == element.NavigableString:
        text = child.text
        attrs = getattr(child.parent, 'attrs')
        classAttrs = attrs.get('class') if attrs.get('class') else []
        if 'furigana' in classAttrs:
          kana = kana + text
        elif 'f_kanji' in classAttrs:
          word = word + text
        else:
          kana = kana + text
          word = word + text
    if not word:
      word = kana
      kana = ''
    words.append([word, kana, level])

levels = [5, 4, 3, 2, 1]
pages = {
  5: 7,
  4: 6,
  3: 18,
  2: 19,
  1: 34,
}

for level in levels:
  for page in range(pages[level]):
    print(level, page + 1)
    getPage(level, page * 100 + 1)

print(len(words))

with open("words.csv", "wt") as fp:
  writer = csv.writer(fp, delimiter=",")
  writer.writerows(words)
