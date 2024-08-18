from bs4 import BeautifulSoup
import requests
import sys
import re

url = sys.argv[1]
page = requests.get(url)
page.encoding = page.apparent_encoding
soup = BeautifulSoup(page.text, features="html.parser")

main = soup.select_one('.main_text')
if main:
  texts = ['' if re.search('○', _) else _ for _ in main.text.strip().splitlines() if _ != '']
  with open('data.txt', 'w', encoding='utf8') as f:
    f.writelines('\n'.join(texts))
