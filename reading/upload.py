from os import environ
from dotenv import load_dotenv
import requests
import sys
import re
from parse import parse
from completions import completions

load_dotenv()
hook = environ.get('hook')
hook_key = environ.get('hook_key')
file_name = sys.argv[1]
t = sys.argv[2]
title = sys.argv[3]
# TODO: 长文翻译质量很差，待优化，长文先关闭翻译
need_trans = False if len(sys.argv) < 5 else sys.argv[4] == '1'

if isinstance(hook, str):
  with open(file_name) as f:
    chapter_texts = f.read().split('\n\n')
    chapters = []
    # chapter由两个换行分割
    for i, chapter_text in enumerate(chapter_texts):
      translations = need_trans and completions(chapter_text) or ''
      if need_trans and not translations:
        print('翻译出错', translations)
        quit()
      translation_list = re.split(r'\n+', translations)
      paragraph_text = chapter_text.split('\n')
      paragraphs = []
      k = 0
      # paragraph由一个换行分割
      for j, paragraph_text in enumerate(paragraph_text):
        if paragraph_text == '':
          continue
        sentences = parse(paragraph_text)
        translation = ''
        if k < len(translation_list):
          translation = translation_list[k]
          k = k + 1
        sentences = list(
          map(
            lambda x: {
              'sections': x,
              'translation': translation,
            },
            sentences,
          )
        )
        paragraphs.append({'sentences': sentences, 'paragraph': j + 1})
      chapters.append({'paragraphs': paragraphs, 'chapter': i + 1})
    r = requests.post(hook, json={"Context":{"argv":{"chapters": chapters, "title": title, "type": t}}}, headers={'AirScript-Token': hook_key})
    print(r.json())
else:
  print("请配置.env文件")
