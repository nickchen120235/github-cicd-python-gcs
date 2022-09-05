from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import json
import os

TYPE = {
  '攻撃力増加': 'atkup',
  '攻撃力減少': 'atkdown',
  '防御力増加': 'defup',
  '防御力減少': 'defdown',

  '火属性効果増加': 'fire',
  '水属性効果増加': 'water',
  '風属性効果増加': 'wind',

  '火属性効果減少': 'firedown',
  '水属性効果減少': 'waterdown',
  '風属性効果減少': 'winddown',

  '劣勢時攻撃効果増加': 'flag',
  '補助スキル発動率増加': 'skillup',
  '補助スキル発動率減少': 'skilldown',

  '通常ダメージ軽減': 'normdown',
  '特殊ダメージ軽減': 'spdown',
  
  'オーダー使用リセット': 'order',
  '全体再編': 'team',
  '前衛再編': 'front',
  '後衛再編': 'back',

  '全体MP回復': 'mprecover',
  'MP軽減': 'mpdown',

  '闇・火属性効果増加': 'firedark',
  '闇・水属性効果増加': 'waterdark',
  '闇・風属性効果増加': 'winddark',

  '光・火属性効果増加': 'firelight',
  '光・水属性効果増加': 'waterlight',
  '光・風属性効果増加': 'windlight',

  '[光闇]属性効果増加': 'lightdark',

  '光属性効果増加': 'light',
  '闇属性効果増加': 'dark',

  '光属性攻撃力増加': 'lightatkup',
  '光属性防御力増加': 'lightdefup',
  '光属性攻撃力減少': 'lightatkdown',
  '光属性防御力減少': 'lightdefdown',

  '闇属性攻撃力増加': 'darkatkup',
  '闇属性防御力増加': 'darkdefup',
  '闇属性攻撃力減少': 'darkatkdown',
  '闇属性防御力減少': 'darkdefdown',

  '水属性攻撃力増加': 'wateratkup',
  '水属性防御力増加': 'waterdefup',
  '水属性攻撃力減少': 'wateratkdown',
  '水属性防御力減少': 'waterdefdown'
}

IGNORED = ['清暉恒風', '女帝蝶の火継', '神渡しの風巻き', '天鳴雨の波紋']

os.environ['PATH'] += os.pathsep + os.getcwd()
options = Options()
options.add_argument('-headless')
print('Loading order page')
drv = webdriver.Firefox(options=options)
drv.get('https://allb.game-db.tw/order')
WebDriverWait(drv, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
html = drv.page_source
soup = bs(html, 'lxml')
drv.quit()

table = soup.find('tbody').find_all('tr')
print(f'[+] Found {len(table)} orders')

def order_value(atk: int, df: int, spatk: int, spdf: int) -> str:
  comp = [atk+df, spatk+spdf, atk+spatk, df+spdf]
  if max(comp) == atk+df: return 'norm'
  elif max(comp) == spatk+spdf: return 'sp'
  elif max(comp) == atk+spatk: return 'atk'
  elif max(comp) == df+spdf: return 'def'
  else: raise Exception('Invalid order type')

orders: dict[str, list] = {}
for row in soup.find('tbody').find_all('tr'):
  name = row.find('td', {'class': 'colName'}).text
  if name in IGNORED: continue
  desc: str = row.find('td', {'class': 'colGvgSkill'}).find('div', {'class': 'sname'}).text
  if 'Lv.2' in desc: continue
  desc: list[str] = desc.split('MP：')
  paid = int(desc[1]) == 0
  desc: str = desc[0].rstrip('Lv.3')

  atk = int(row.find('td', {'class': 'colPAtk'}).text)
  df = int(row.find('td', {'class': 'colPDef'}).text)
  spatk = int(row.find('td', {'class': 'colMAtk'}).text)
  spdf = int(row.find('td', {'class': 'colMDef'}).text)
  value = order_value(atk, df, spatk, spdf)

  t = TYPE[desc[3:] if len(desc.split(':')) > 1 else desc] + ('norm' if desc.split(':')[0] == '通常' else 'sp' if desc.split(':')[0] == '特殊' else '')

  try:
    orders[t]
  except KeyError:
    orders[t] = []

  wt = int(row.find('td', {'class': 'colGvgSkillLead'}).text)
  at = int(row.find('td', {'class': 'colGvgSkillDur'}).text)
  img = f'https://allb.game-db.tw{row.find("td", {"class": "colIcon"}).find("img")["src"]}'
  orders[t].append({
    'name': name,
    'desc': desc,
    'paid': paid,
    'value': value,
    'wt': wt,
    'at': at,
    'img': img
  })

print(f'[+] Done.')
with(open('orders.json', 'w', encoding='utf-8')) as f:
  json.dump(orders, f, ensure_ascii=False, indent=2)