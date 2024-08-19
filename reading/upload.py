from os import environ
from dotenv import load_dotenv
import requests
import sys
from parse import parse

load_dotenv()
hook = environ.get('hook')
hook_key = environ.get('hook_key')
collect_tags = ['VERB', 'NOUN', 'ADV', 'ADJ', 'DET', 'NUM']
file_name = sys.argv[1]
t = sys.argv[2]
title = sys.argv[3]

def newSentence(i, j):
  return {'text': '', 'sections': [], 'words': [], 'chapter': i + 1, 'paragraph': j + 1}

if isinstance(hook, str):
  with open(file_name) as f:
    chapter_texts = f.read().split('\n\n')
    chapters = []
    # chapter由两个换行分割
    for i, chapter_text in enumerate(chapter_texts):
      paragraph_text = chapter_text.split('\n')
      chapter = []
      # paragraph由一个换行分割
      for j, paragraph_text in enumerate(paragraph_text):
        if paragraph_text == '':
          continue
        result = parse(paragraph_text)
        sentences = []
        sentence = newSentence(i, j)
        for word in result:
          section = ''
          is_end = False
          for token in word['tokens']:
            if token['text'] == '。':
              is_end = True
              break
            section = section + token['text']
            if token['tag'] in collect_tags:
              sentence['words'].append({'base': token['base'], 'kana': token['kana']})
          sentence['sections'].append(section)
          sentence['text'] = sentence['text'] + section
          if is_end:
            sentences.append(sentence)
            sentence = newSentence(i, j)
        if sentence['text']:
          sentences.append(sentence)
        chapter.append(sentences)
      chapters.append(chapter)
    r = requests.post(hook, json={"Context":{"argv":{"chapters": chapters, "title": title, "type": t}}}, headers={'AirScript-Token': hook_key})
    print(r.json())
else:
  print("请配置.env文件")
