from os import environ
from dotenv import load_dotenv
import requests
import sys
from parse import parse
from completions import completions

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
      translations = completions(chapter_text)
      if not translations:
        print('翻译出错', translations)
        quit()
      translations = translations.split('\n')
      paragraph_text = chapter_text.split('\n')
      chapter = []
      # paragraph由一个换行分割
      for j, paragraph_text in enumerate(paragraph_text):
        if paragraph_text == '':
          continue
        paragraph_translation = translations[j].split('。')
        k = 0
        result = parse(paragraph_text)
        sentences = []
        sentence = newSentence(i, j)
        for word in result:
          section = ''
          text = ''
          is_end = False
          for token in word['tokens']:
            if token['text'] == '。':
              is_end = True
              break
            text = text + token['text']
            section = section + token['text'] + ('(' + token['kana'] + ')' if token['base'] != token['kana'] else '')
            if token['tag'] in collect_tags:
              sentence['words'].append({'base': token['base'], 'kana': token['kana']})
          sentence['sections'].append(section)
          sentence['text'] = sentence['text'] + text
          if is_end:
            sentence['translation'] = paragraph_translation[k]
            k = k + 1
            sentences.append(sentence)
            sentence = newSentence(i, j)
        if sentence['text']:
          sentence['translation'] = paragraph_translation[k]
          k = k + 1
          sentences.append(sentence)
        chapter.append(sentences)
      chapters.append(chapter)
    r = requests.post(hook, json={"Context":{"argv":{"chapters": chapters, "title": title, "type": t}}}, headers={'AirScript-Token': hook_key})
    print(r.json())
else:
  print("请配置.env文件")
