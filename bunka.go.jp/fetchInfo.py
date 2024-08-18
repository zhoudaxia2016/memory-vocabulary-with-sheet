from bs4 import BeautifulSoup
import requests
import re
import json

def fetchInfo(url):
  page = requests.get(url)
  page.encoding = page.apparent_encoding
  soup = BeautifulSoup(page.text, features="html.parser")
  text = soup.select('script[type="application/ld+json"]')[0].text
  text = re.sub(r'\s+', '', text)
  data = json.loads(text)
  properties = data[2]['additionalProperty']
  article = [_ for _ in properties if _['@type'] == 'Article'][0]
  ondoku = [_ for _ in article['additionalProperty'] if _['name'] == '音読み'][0]
  kundoku = [_ for _ in article['additionalProperty'] if _['name'] == '訓読み'][0]
  if type(ondoku) == str:
    ondoku = [ondoku]
  if type(kundoku) == str:
    kundoku = [kundoku]
  return {'ondoku': ondoku, 'kundoku': kundoku}
