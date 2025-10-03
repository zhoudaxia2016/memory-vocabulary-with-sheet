import requests
import re
import csv
from concurrent.futures import ThreadPoolExecutor
from api import upload, getRecords, getKanjis
import sys

headers = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
}
url = 'https://mazii.net/api/search'

classMap = {
  'aux-adj': '助动词',
  'aux-v': '助动词',
  'adj-i': '形容词',
  'adj-ix': '形容词',
  'adj-na': '形容动词', 
  'prt': '助词',
  'num': '数词',
  'ctr': '量词',
  'pref': '接头辞',
  'n-pref': '接头辞',
  'n-suf': '接尾辞',
  'suf': '接尾辞',
  'aux': '助动词',
  'pn': '代词',
  'n': '名词',
  'n-t': '名词',
  'v1': '动词',
  'v5': '动词',
  'n-adv': '名词',
  '∫': '连体词',
  'adj-pn': '连体词',
  'adv': '副词',
  'conj': '接续词',
  'int': '感叹词',
}
weightMap = {}
i = 0
for k in classMap.keys():
  weightMap[k] = i
  i = i + 1

verbTypeMap = {
  'v5': '五段动词',
  'v1': '上下段动词',
}

typeMap = {
  'n-t': '时间',
}

transitiveMap = {
  'vt': '他动词',
  'vi': '自动词'
}

def req(query):
  res = requests.post(url, json={
    'dict': 'jacn',
    'type': 'word',
    'query': query,
    'limit': 20,
    'page': 1
  }, headers=headers)
  return res.json()

def matchKana(phonetic, kana):
  return type(phonetic) == str and kana in phonetic.split(' ')
[].index

def find(arr, fn):
  for v in arr:
    if (fn(v)):
      return v

def search(index, word, kana = '', level = ''):
  if not kana:
    kana = word
  try:
    data = req(word)
  except:
    data = req(word)
  d = None
  for v in data['data']:
    # 如果单词是全假名，则比较单词和读音是否相同
    if (re.match(r'^[\u3040-\u309FF\u30A0-\u30FF]+$', word)):
      if (v.get('phhonetic')):
        phhonetic = re.sub(r'\/|\\', '', v.pronunciation[0].transcriptions[0].kana) if re.match(r'\s', v.phhonetic) else v.phhonetic
        if (matchKana(phhonetic, word)):
          d = v
          break
    # 如果是单词有汉字，则比较单词与word，还有假名与读音
    if word == v['word'] and (not kana or matchKana(v['phonetic'], kana)):
      d = v
      break

  if not d:
    if (len(data['data']) == 0):
      print('搜不到单词', word, kana)
      return
    d = data['data'][0]
  short_mean = d['short_mean']
  means = d['means']
  cl = ''
  example = None
  exampleTranslation = ''
  t = ''
  trans = ''
  for m in means:
    if (not m.get('kind')):
      continue
    ts = m['kind'].split(', ')
    if (find(ts, lambda _ : _.startswith('v5'))):
      cl = 'v5'
    else:
      cls = list(_ for _ in ts if classMap.get(_))
      cls.sort(key=lambda elem : weightMap.get(elem))
      if cls:
        cl = cls[0]
    if (cl):
      if (m.get('examples') and len(m['examples']) > 0):
        example = m['examples'][0]['content']
        exampleTranslation = m['examples'][0]['mean']
      t = find(ts, lambda _ : typeMap.get(_))
      trans = find(ts, lambda _ : transitiveMap.get(_))
      break
  if not example:
    dd = find(data['data'], lambda a : find(a['means'], lambda b : b.get('examples') and len(b['examples']) > 0))
    if dd:
      mean = find(dd['means'], lambda _ : _.get('examples') and len(_['examples']) > 0)
      if mean:
        example = mean['examples'][0]['content']
        exampleTranslation = mean['examples'][0]['mean']
  shortMeans = short_mean.split('; ')
  shortMean = find(shortMeans, lambda _ : not re.match(r'[\u3040-\u309FF\u30A0-\u30FF]', _) or shortMeans[0])
  fields = {
    '详解': short_mean,
    '词性': classMap.get(cl, ''),
    '动词活用分类': verbTypeMap.get(cl, ''),
    '例句': example or '',
    '例句翻译': exampleTranslation or '',
    '分类': [typeMap.get(t)] if typeMap.get(t) else [],
    '释义': shortMean,
    '自他性': transitiveMap.get(trans, ''),
    '假名': kana,
    '单词': word,
  }
  if level != '':
    fields['等级'] = level
  if (not kana and type(d['phonetic']) == str):
    fields['假名'] = d['phonetic'].split(' ')[0]

  name = word
  kana = fields.get('假名', kana)
  kanjiIds = []
  j = 0
  for i in range(len(name)):
    if (re.match(r'[^\u3040-\u309F\u30A0-\u30FFa-zA-Z]', name[i])):
      m = kanjiMap.get(name[i])
      if (not m):
        continue
      items = list(m.items())
      fk = find(items, lambda x : kana[j:].startswith(x[0]))
      if (not fk):
        fk = find(items, lambda x : kana[j:].startswith(x[1]['kana']))
      if (not fk):
        continue
      kanjiIds.append(fk[1]['id'])
      j = j + len(fk[0])
    else:
      j = j + 1
  fields['关联汉字'] = {'recordIds': kanjiIds}
  return {'fields': fields}

kanjiMap = getKanjis()
def find_duplicates(lst):
  seen = set()
  duplicates = set()
  for item in lst:
    if item in seen:
      duplicates.add(item)
    else:
      seen.add(item)
  return list(duplicates)
with ThreadPoolExecutor(50) as executor:
  print(executor._max_workers)
  file_name = sys.argv[1]
  sheet_name = sys.argv[2]
  delimiter = sys.argv[3] if len(sys.argv) > 3 else ","
  with open(file_name, "r") as fp:
    reader = csv.reader(fp, delimiter=delimiter)
    i = 0
    result = []
    n = 2
    step = 2000
    for line in reader:
      if (i < (n - 1) * step or i >= n * step):
        i = i + 1
        continue
      level = len(line) == 3 and line[2] or ''
      result.append(executor.submit(search, i, line[0], len(line) == 1 and line[0] or line[1], level))
      i = i + 1
    words = []
    currentRecords = getRecords(sheet_name)
    seen = set()
    for r in currentRecords:
      seen.add(r['fields']['单词'])
    for item in result:
      word = item.result()
      if word == None or word['fields']['单词'] in seen:
        continue
      words.append(word)
      seen.add(word['fields']['单词'])
    print(len(words))
    upload(sheet_name, words)
