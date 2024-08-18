import spacy
import jaconv
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
  sections = []
  doc = nlp(text)
  size = len(doc)
  i = 0
  while i < size:
    token = doc[i]
    head = token.head
    if token.pos_ == 'SPACE':
      pass
    elif token.dep_ in skip_heads or token == head or (token.dep_ in skip_heads2 and abs(head.i - i) > 1):
      sections.append({'tokens': [token], 'i': i})
    elif head.i > i:
      tokens = []
      for k in range(i, head.i + 1):
        tokens.append(doc[k])
      sections.append({'tokens': tokens, 'i': i})
      i = head.i
    else:
      j = len(sections) - 1
      merge = [token]
      while j > -1:
        merge = sections[j]['tokens'] + merge
        if sections[j]['i'] <= head.i:
          break
        j = j - 1
      sections = sections[:j]
      sections.append({'tokens': merge, 'i': merge[0].i})
    i = i + 1

  for i in range(0, len(sections)):
      section = sections[i]
      section['tokens'] = list(map(handle_token, section['tokens']))
  return sections
