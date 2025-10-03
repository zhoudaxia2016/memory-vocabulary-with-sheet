import requests
from dotenv import load_dotenv
from os import environ
load_dotenv()

hook_key = environ.get('hook_key')
hook_createrecords = environ.get('hook_createrecords')
hook_getrecords = environ.get('hook_getrecords')

def upload(sheetName, records):
  argv = {'sheetName': sheetName, 'records': records}
  res = requests.post(hook_createrecords, json={'Context': {'argv': argv}}, headers={'AirScript-Token': hook_key})
  print(res.text)

def getRecords(sheetName):
  result = []
  offset = None
  while (True):
    argv = {"sheetName": sheetName}
    if (offset):
      argv['offset'] = offset
    print('get records ', argv)
    res = requests.post(hook_getrecords, json={'Context': {'argv': argv}}, headers={'AirScript-Token': hook_key})
    data = res.json()['data']['result']
    if not data.get('records'):
      break
    result = result + data['records']
    if not data.get('offset'):
      break
    offset = data['offset']
  return result

def getKanjis():
  result = getRecords('汉字')
  kanjiMap = {}
  for kj in result:
    name = kj['fields']['字']
    kana = kj['fields']['假名']
    fullKana = kj['fields']['完整假名']
    r = kanjiMap.get(name, {})
    r[fullKana] = {'id': kj['id'], 'kana': kana}
    kanjiMap[name] = r
  return kanjiMap
