import requests
from os import environ
from dotenv import load_dotenv
load_dotenv()
completions_url = environ.get('completions_url')
completions_key = environ.get('completions_key')
completions_model = environ.get('completions_model')

prompt = '''
你是一个熟悉日语的大模型，请将下面日语歌词翻译成中文（输出的行数要和输入的行数一致）：
'''

def completions(text):
  if not completions_url:
    print('请配置completions_url')
    return
  res = requests.post(completions_url, json={
    'model': completions_model,
    'messages': [
      {
        'role': 'user',
        'content': prompt + text,
      }
    ]
  }, headers={'Authorization': completions_key, 'content-type': 'application/json'})
  res =  res.json()
  print(res)
  result = res['choices'][0]['message']['content']
  print('消耗tokens: ', res['usage']['total_tokens'])
  return result
