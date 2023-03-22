import requests
from bs4 import BeautifulSoup
import warnings


class EHentaiApi:
    def __init__(self):
        self.base_url = "https://e-hentai.org/"
        self.proxies = {
            'http': 'http://127.0.0.1:7890/',
            'https': 'http://127.0.0.1:7890/'
        }
        self.headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/111.0.0.0 Safari/537.36'
        }
        self.length_limit = 5

    def search(self, query):
        """

        :param query: search keyword
        :return: Json, {"title":"","url":""}
        """

        url = self.base_url + "?f_search={}".format(query)
        try:
            r = requests.get(url=url, proxies=self.proxies, headers=self.headers)
        except:
            return [{
                "error": "访问ehentai失败"
            }]

        # fp = open('./pica.html', 'r', encoding='UTF-8')

        with warnings.catch_warnings(record=True) as w:
            bf = BeautifulSoup(r.text, "lxml")

            if len(w) > 0:
                return [{
                    "error": "访问被ehentai限制"
                }]

        my_list = bf.find_all("div", class_="glthumb")
        return_val = []
        cnt = min(len(my_list), self.length_limit)

        for i in range(0, cnt):
            item = my_list[i]
            img_label = item.find_all("img")[0]
            title = img_label['title']
            if 'data-src' in img_label.attrs:
                url = img_label['data-src']
            else:
                url = img_label['src']
            return_val.append({
                'title': title,
                'url': url
            })

        return return_val

    def generate_msg(self, meta_msg):
        """

        :param meta_msg: Json List
        :return: generated message
        """

        if len(meta_msg) == 0:
            return ""

        search_info = {
            "title": "",
            "url": ""
        }
        error_info = {
            "error":""
        }
        msg = ""

        if meta_msg[0].keys() == search_info.keys():
            for item in meta_msg:
                msg = msg + item["title"] + "\n"
                msg = msg + "[CQ:image,file={}]".format(item["url"]) + "\n"
        elif meta_msg[0].keys() == error_info.keys():
            for item in meta_msg:
                msg = msg + item["error"] + "\n"


        return msg


if __name__ == "__main__":
    obj = EHentaiApi()
    print(obj.generate_msg(obj.search("Alice")))
