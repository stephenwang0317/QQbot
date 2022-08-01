import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
}
fp = open("./塔菲按钮.html", 'r', encoding="UTF-8")
bf = BeautifulSoup(fp, "lxml")
list1 = bf.find_all("a", "btn")
for item in list1:
    if len(item.find_all("span", "text")) == 0:
        continue
    name = item.find_all("span", "text")[0].string
    url = item.get("href")
    r = requests.get(url=url, headers=headers)
    with open("./"+name+".mp3", "wb") as fp:
        fp.write(r.content)
        fp.close()
        print("over")
