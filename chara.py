from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
from datetime import date
import json
import os

TYPE_DICT = {
  '通単': 'normsingle',
  '通範': 'normmulti',
  '特単': 'spsingle',
  '特範': 'spmulti',
  '支援': 'buff',
  '妨害': 'debuff',
  '回復': 'heal'
}

os.environ['PATH'] += os.pathsep + os.getcwd()
options = Options()
options.add_argument('-headless')
print('Loading chara page')
drv = webdriver.Firefox(options=options)
drv.get('https://allb.game-db.tw/chara')
WebDriverWait(drv, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))
html = drv.page_source
# drv.quit()

soup = bs(html, 'lxml')
charas =  soup.body.find('div', {'class': 'pFull'}).find_all('div', {'class': 'jss1'})
print(f'[+] Found {len(charas)} characters')

all_clothes = {}
for chara in charas:
  print()
  name = chara.find('div', {'class': 'jss4'}).text
  print(f'[i] Current character: {name}')
  # drv = webdriver.Firefox(options=options)
  drv.get(f'https://allb.game-db.tw/{chara.find("a")["href"][1:]}')
  WebDriverWait(drv, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'charaAbility')))
  html = drv.page_source
  # drv.quit()
  chara_page = bs(html, 'lxml')
  clothes_raw = chara_page.body.find('div', {'class': 'pFull'}).find_all('a', {'class': 'jss1'})
  print(f'[+] Found {len(clothes_raw)} clothes')

  clothes = []
  for c in clothes_raw:
    if '12.5' in c.find('div', {'class': 'charaAbility'}).find('span', {'class': 'skilldesc'}).text or '15' in c.find('div', {'class': 'charaAbility'}).find('span', {'class': 'skilldesc'}).text:
      desc: str = c.find('div', {'class': 'charaAbility'}).find('span', {'class': 'skilldesc'}).text
      t = TYPE_DICT[desc.split('+')[0]]
      img = f"https://allb.game-db.tw{c.find('img')['src']}"
      alt = c.find('img')['alt']
      clothes.append({
        'type': t,
        'img': img,
        'alt': alt
      })
  
  print(f'[+] Done. {len(clothes)} 12.5% clothes')
  assert len(clothes) <= len(clothes_raw)
  all_clothes[name] = clothes

drv.quit()

output = {
  'lastUpdated': str(date.today()),
  'clothes': all_clothes
}

with open('clothes.json', 'w') as f:
  f.write(json.dumps(output, indent=2, ensure_ascii=False))
