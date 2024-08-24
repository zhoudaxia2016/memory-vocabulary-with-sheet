import spacy
import re
import pykakasi

kks = pykakasi.kakasi()
nlp = spacy.load("ja_core_news_lg")

skip_heads = ['advcl', 'obj', 'nmod', 'acl', 'obl', 'cc', 'cop', 'nsubj', 'dep', 'advmod']
skip_heads2 = ['compound']

def handle_token(token):
  info = token.pos_
  result = re.match(r'(Inflection=([^|]+)\|)?Reading=([^|]+)', str(token.morph))
  tag = token.pos_

  if token.tag_.split('-')[0] == '補助記号':
    tag = 'PUNCT'
  if result is not None:
    info = result[2]
  return {
    'text': token.text,
    'tag': tag,
    'info': info,
    'kana': ''.join([_['hira'] for _ in kks.convert(token.lemma_)]),
    'base': token.lemma_,
  }

def parse(text):
  sentences = []
  doc = nlp(text)
  size = len(doc)
  i = 0
  sentence = []
  while i < size:
    token = doc[i]
    head = token.head
    if token.pos_ == 'SPACE':
      pass
    elif token.text == '。':
      sentences.append(sentence)
      sentence = []
    elif token.dep_ in skip_heads or token == head or (token.dep_ in skip_heads2 and abs(head.i - i) > 1):
      sentence.append({'tokens': [token], 'i': i, 'dep': token.dep_})
    elif head.i > i:
      tokens = []
      for k in range(i, head.i + 1):
        tokens.append(doc[k])
      sentence.append({'tokens': tokens, 'i': i, 'dep': token.dep_})
      i = head.i
    else:
      j = len(sentence) - 1
      merge = [token]
      while j > -1:
        merge = sentence[j]['tokens'] + merge
        if sentence[j]['i'] <= head.i:
          break
        j = j - 1
      sentence = sentence[:j]
      sentence.append({'tokens': merge, 'i': merge[0].i, 'dep': token.dep_})
    i = i + 1

  if len(sentence) > 0:
    sentences.append(sentence)
  for sentence in sentences:
    for section in sentence:
      section['tokens'] = list(map(handle_token, section['tokens']))
  return sentences
