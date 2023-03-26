import requests
from bs4 import BeautifulSoup


class Info:

    def __call__(self, param: dict) -> str:
        msg = ""
        for key, value in param.items():
            if key == "img":
                msg = msg + "[CQ:image,file={}]".format(value) + '\n'
            else:
                msg = msg + key + ": " + value + '\n'
        msg = msg + "-----------\n"
        return msg


class JavDb:
    def __init__(self):
        self.proxies = {
            'http': 'http://127.0.0.1:7890/',
            'https': 'http://127.0.0.1:7890/'
        }
        self.headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/111.0.0.0 Safari/537.36',
            "cookie": "list_mode=h; theme=auto; locale=zh; over18=1; __cf_bm=1JVuuBIZ0ntcuPDumKtMp1_5QIEW4oy6P1r6yt28y9"
                      "I-1679736315-0-ATC5cB+ceSLT8vsjq0+c5OFdZkOC2+uEp14Fx0DlJoTLj6jCO3AzBSUBVcFRL0R453iZaqNQmJqhRWGzc"
                      "QcasGb87UVcK+LZAWvf1KtzSjqZoLwN3lUxsWxpki4vwJnAYA==; _ym_uid=1679736315823558314; _ym_d=16797363"
                      "15; _ym_isad=2; _jdb_session=Xao3L31LX5ZelLqomNY3P+RaLgrsIXoamkO+dtplRWpm3374+/BYp8+XqNac7sIYFht"
                      "a0cLXL+1Iq+jLDBWzd9B5nCAEP+qzC7zAGP9dqeuAuFODlzogroy54a6elXgPmESaWMqfO5gS0TEJ0QFejjnK/l5ZKQllWIv"
                      "uqr76TCbkm2hVJhHyC1S1y+Zdj3r1xWcz1q99KBfPLXN+dWwgRJVvW1Q/DcNMO+d9bf13OPCibuLDVRKrg42aDE3XLKs+GxV"
                      "18VDtTQ9BTPwn7XTBoCnJfVkOq3An+Bm5RGJgUzvx+Z7BHadfRvM2--Y8ZqSsPnfSab6REQ--6n6DzNdHGPC/c7nDsx0eOw="
                      "="
        }
        self.limit = 5
        self.info = Info()

    def get_cover(self, query):
        url = "https://javdb.com/search?q={}".format(query)
        try:
            r = requests.get(timeout=5, url=url, headers=self.headers, proxies=self.proxies)
        except:
            return self.info({"error": "访问失败"})

        bf = BeautifulSoup(r.text, "lxml")
        item_list = bf.find_all("div", class_="item")
        msg = ""

        number = min(self.limit, len(item_list))
        for i in range(0, number):
            item = item_list[i].find("a")
            title_tag = item.find('div', class_="video-title")
            title = title_tag.find('strong').string + "," + title_tag.contents[1]
            img = item.find("div", class_="cover").find("img").get("src")
            # print(item)
            score = item.find("div", class_="score").find("span").contents[1]
            msg += self.info({
                "title": title,
                "score": score.replace("\n", '').replace(' ', ''),
                "img": img
            })

        return msg

    def choose_fun(self, params: list) -> str:
        if len(params) == 1:
            return self.info({
                "error": "缺少查询参数"
            })
        else:
            return self.get_cover(params[1])

