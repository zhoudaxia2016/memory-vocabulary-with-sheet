# 常用汉字表，2136个字，4688个读音
# 地址: https://www.bunka.go.jp/kokugo_nihongo/sisaku/joho/joho/kijun/naikaku/kanji/joyokanjisakuin/index.html

from bs4 import BeautifulSoup, Tag
import requests
import re
import csv
import os

url = 'https://www.bunka.go.jp/kokugo_nihongo/sisaku/joho/joho/kijun/naikaku/kanji/joyokanjisakuin/index.html'

generateHanji = os.path.exists('./kanji2Hanji.txt')
kanjiMap = {}
if generateHanji:
  for l in open('./kanji2Hanji.txt'):
    res = l.split(' ')
    kanjiMap[res[1].strip()] = res[0]

page = requests.get(url)
page.encoding = page.apparent_encoding
soup = BeautifulSoup(page.text, features="html.parser")

table = soup.find('table', class_='display')
hirakanaPat = r'[\u3040-\u309F]'
katakanaPat = r'[\u30A0-\u30FF]'

def toHirakana(kana):
  return re.sub(katakanaPat, lambda m : chr(ord(m.group()) - 0x60), kana)

with open('data.csv', 'w', encoding='utf-8-sig', newline="") as f:
  writer = csv.writer(f)
  writer.writerow(['字', '假名', '送假名', '旧字体', '音训读', '简体字'])
  if isinstance(table, Tag):
    trs = [tr for tr in table.findAll('tr')]
    words = []
    for tr in trs:
      tds = tr.find_all('td')
      if len(tds) == 4:
        char = tds[0].text
        oldChar = ''
        if len(char) > 1:
          m = re.match(r'(.*)（(\w)）', char)
          if m:
            char = m.group(1)
            oldChar = m.group(2)
        hanji = generateHanji and kanjiMap.get(char, '') or ''
        for i, kana in enumerate(tds[1].get_text(strip=True, separator='\n').splitlines()):
          isKundo = re.search(hirakanaPat, kana)
          lines = tds[2].get_text(strip=True, separator='\n').splitlines()
          wholeWord = len(lines) > i and lines[i].split('，')[0] or ''
          m = re.match(r'\w+?([\u3040-\u309F]+)', wholeWord)
          hirakana = isKundo and kana or toHirakana(kana)
          okurikana = m and m.group(1) or ''
          okurikana = re.match(r'\w+' + okurikana, hirakana) and okurikana or ''
          hirakana = re.sub(okurikana + r'$', '', hirakana)
          words.append([char, hirakana, okurikana or '', oldChar, isKundo and '训读' or '音读', hanji])
    writer.writerows(words)
