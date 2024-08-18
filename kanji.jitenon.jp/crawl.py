from bs4 import BeautifulSoup, Tag
import requests
import re
import csv
import os
import json

baseurl = 'https://kanji.jitenon.jp/cat/kyu%.html'

grades = []
jgrades = []

hirakanaPat = r'[\u3040-\u309F]'
katakanaPat = r'[\u30A0-\u30FF]'

def toHirakana(kana):
  return re.sub(katakanaPat, lambda m : chr(ord(m.group()) - 0x60), kana)

def fetchInfo(url):
  print('url', url)
  page = requests.get(url)
  page.encoding = page.apparent_encoding
  soup = BeautifulSoup(page.text, features="html.parser")
  text = soup.select('script[type="application/ld+json"]')[0].text
  text = re.sub(r'\s+', '', text)
  data = json.loads(text)
  print(data)
  article = [_ for _ in data if _['@type'] == 'Article'][0]
  ondokuO = [_ for _ in article['additionalProperty'] if _['name'] == '音読み']
  ondoku = len(ondokuO) > 0 and ondokuO[0]['value'] or []
  kundokuO = [_ for _ in article['additionalProperty'] if _['name'] == '訓読み']
  kundoku = len(kundokuO) > 0 and kundokuO[0]['value'] or []
  if type(ondoku) == str:
    ondoku = [ondoku]
  if type(kundoku) == str:
    kundoku = [kundoku]
  ondoku = [toHirakana(re.sub(r'（|）', '', _)) for _ in ondoku]
  kundoku_ = []
  for _ in kundoku:
    m = re.match(r'(\w+)(（\w+）)', _)
    if m:
      kundoku_.append({'kana': m.group(1), 'okurikana': re.sub(r'（|）', '', m.group(2))})
    else:
      kundoku_.append({'kana': _, 'okurikana': ''})
  return {'ondoku': ondoku, 'kundoku': kundoku_}

def fetch(url):
  print('爬取url: ', url)
  page = requests.get(url)
  page.encoding = page.apparent_encoding
  soup = BeautifulSoup(page.text, features="html.parser")
  items = [{'text': _.text, 'url': _.select('a')[0].attrs['href']} for _ in soup.select('.search_parts li')]
  print(len(items))
  return items

for i in range(2, 11):
  i = i < 10 and '0' + str(i) or str(i)
  url = re.sub('%', i, baseurl)
  grades.append(fetch(url))

for i in range(1, 3):
  i = i < 10 and '0' + str(i) or str(i)
  url = re.sub('%', i + 'j', baseurl)
  jgrades.append(fetch(url))

jimmeiUrl = 'https://kanji.jitenon.jp/cat/jimmei.html'
jimmei = fetch(jimmeiUrl)
joyo = []
joyoMap = {}
jimmeiMap = {}
for _ in jimmei:
  jimmeiMap[_['text']] = _

with open('../bunka.go.jp/data.csv') as f:
  joyo = csv.reader(f)
  for _ in joyo:
    joyoMap[_[0]] = joyoMap.get(_[0]) and joyoMap[_[0]] or {'value': []}
    joyoMap[_[0]]['value'].append(_)

generateHanji = os.path.exists('../bunka.go.jp/kanji2Hanji.txt')
kanjiMap = {}
if generateHanji:
  for l in open('./kanji2Hanji.txt'):
    res = l.split(' ')
    kanjiMap[res[1].strip()] = res[0]

def append(w, g):
  text = w['text']
  if joyoMap.get(text):
    for _ in joyoMap[text]['value']:
      rows.append(_ + [g, '常用汉字'])
    joyoMap[text]['added'] = True
  elif jimmeiMap.get(text):
    info = fetchInfo(w['url'])
    jimmeiMap[text]['added'] = True
    for ondoku in info['ondoku']:
      rows.append([text, ondoku, '', '', '音读', kanjiMap.get(text), g, '人名用汉字'])
    for kundoku in info['kundoku']:
      rows.append([text, kundoku['kana'], kundoku['okurikana'], '', '训读', kanjiMap.get(text), g, '人名用汉字'])
  else:
    info = fetchInfo(w['url'])
    for ondoku in info['ondoku']:
      rows.append([text, ondoku, '', '', '音读', kanjiMap.get(text), g, ''])
    for kundoku in info['kundoku']:
      rows.append([text, kundoku['kana'], kundoku['okurikana'], '', '训读', kanjiMap.get(text), g, ''])

with open('./data.csv', 'w', encoding='utf-8-sig', newline='') as f:
  writer = csv.writer(f)
  writer.writerow(['字', '假名', '送假名', '旧字体', '音训读', '简体字', '等级', '类别'])
  rows = []
  for i, data in enumerate(grades):
    g = str(i + 2) + '级'
    for _ in data:
      append(_, g)
  for i, data in enumerate(jgrades):
    g = '准' + str(i + 1) + '级'
    for _ in data:
      append(_, g)
  for text, value in joyoMap.items():
    if value.get('added') != True:
      for _ in value['value']:
        rows.append(_ + ['', '常用汉字'])
  for text, value in jimmeiMap.items():
    if value.get('added') != True:
      info = fetchInfo(value['url'])
      for ondoku in info['ondoku']:
        rows.append([text, ondoku, '', '', '音读', '', '', '人名用汉字'])
      for kundoku in info['kundoku']:
        rows.append([text, kundoku['kana'], kundoku['okurikana'], '', '训读', '', '', '人名用汉字'])
  writer.writerows(rows)
