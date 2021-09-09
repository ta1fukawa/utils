import re
import requests
import mojimoji
from bs4 import BeautifulSoup

def sample():
    city_saigai = CitySaigai()
    print(city_saigai.get())

class CitySaigai(object):
    def __init__(self):
        self.session = requests.session()

    def get(self):
        r = self.session.get('https://sc.city.kawasaki.jp/saigai/index.htm')
        assert r.status_code == requests.codes.ok
        r.encoding = 'Shift-JIS'

        bs = BeautifulSoup(r.text, 'html.parser')
        items = bs.find('table').findAll('tr')

        texts = list()
        for item in items:
            text = item.get_text().strip()
            text = text.replace('、', '')
            text = text.replace('。', '')
            text = text.replace('　', '')

            if len(text) == 0 or '市内に災害は発生しておりません' in text:
                break

            time, place, _, event, _ = re.findall('^(.+)頃(.+)付近(より|で発生した)(.+)(しています|しました|でした).*$', text)[0]
            texts.append((mojimoji.zen_to_han(time), place, event))

        return texts
