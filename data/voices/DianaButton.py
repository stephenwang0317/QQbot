import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    "cookie": "__cf_bm=zw5EOkhC1CkPS1vlYPVPd7YjPSe2d_1vGkWc2JFZI_Y-1658641904-0-AQbmw+8s/aY2zRUIa4+d9V4GkCNBZLS+eM1xklTFJXIMyGfoE1KP5ftqA/BGcrkQkXBL/dKFZH7MH2hL+fh5lQKj9oj2sb2Ae22WOTAW2fdM6mc3XUYC/nUmjpCMcaOOrw=="
}
url = "https://vtbkeyboard.moe/api/get_vtb_page?uid=672328094"
r = requests.get(url=url)
voiceTypeList = r.json()['data']['voices']
for x in voiceTypeList:
    for item in x['voiceList']:
        name = item['name']
        url = item['path']
        r2 = requests.get(url=url)
        with open(name+".mp3", "wb") as fp:
            fp.write(r2.content)
        print(name+"\t\tover")
        
