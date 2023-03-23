import requests
from bs4 import BeautifulSoup
import warnings


class SearchInfo:
    def __init__(self, title, img, page):
        self.title = title
        self.img = img
        self.page = page

    def serialize(self):
        msg = ""
        msg = msg + self.title + "\n"
        msg = msg + "[CQ:image,file={}]".format(self.img) + "\n"
        msg = msg + "链接: " + self.page + "\n"
        return msg


class ErrorInfo:
    def __init__(self, error):
        self.error = error

    def serialize(self):
        msg = ""
        msg = msg + self.error + "\n"
        return msg


class HelpInfo:
    def __init__(self, dict2: dict):
        self.dict = dict2

    def serialize(self):
        msg = ""
        for a, b in self.dict.items():
            msg = msg + b[1] + "\n"

        return msg


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
        self.search_length_limit = 5
        self.top_length_limit = 10
        self.fun_map = {
            "s": [self.search, "/本子 s 名字，搜索特定本子"],
            "top": [self.get_top, "/本子 top，获取热门"],
            "help": [self.get_help, "/本子 help，获取帮助"]
        }

    def search(self, param) -> str:
        """

        :param param: List[p1,p2,...,pn], px:str
        :param query: search keyword
        :return: Json, {"title":"","url":""}
        """
        query = param[2]
        url = self.base_url + "?f_search={}".format(query)
        return self.generate_msg(self.get_page(url=url, limit=self.search_length_limit))

    def generate_msg(self, meta_msg) -> str:
        """

        :param meta_msg: Json List
        :return: generated message
        """

        if len(meta_msg) == 0:
            return ""

        msg = ""

        for item in meta_msg:
            msg = msg + item.serialize()

        return msg

    def get_page(self, url, limit) -> list:
        try:
            r = requests.get(url=url, proxies=self.proxies, headers=self.headers)
        except:
            return [ErrorInfo("访问ehentai失败")]

        # fp = open('./pica.html', 'r', encoding='UTF-8')

        with warnings.catch_warnings(record=True) as w:
            bf = BeautifulSoup(r.text, "lxml")

            if len(w) > 0:
                return [ErrorInfo("访问被ehentai限制")]

        my_list = bf.find_all("div", class_="glthumb")
        list2 = [item.find_all("a")[0]["href"] for item in bf.find_all("td", class_="gl3c glname")]

        return_val = []
        cnt = min(len(my_list), limit)

        for i in range(0, cnt):
            item = my_list[i]
            page_url = list2[i]
            img_label = item.find_all("img")[0]
            title = img_label['title']

            if 'data-src' in img_label.attrs:
                url = img_label['data-src']
            else:
                url = img_label['src']

            return_val.append(SearchInfo(title=title, img=url, page=page_url))

        return return_val

    def get_top(self, params) -> str:
        top_url = "https://e-hentai.org/popular"
        return self.generate_msg(self.get_page(url=top_url, limit=self.top_length_limit))

    def get_help(self, params) -> str:
        obj = HelpInfo(self.fun_map)
        return obj.serialize()

    def choose_fun(self, params: list) -> str:
        func = self.fun_map.get(params[1])
        if func is None:
            return self.generate_msg([ErrorInfo("未知命令")])
        else:
            func = func[0]

        return func(params)


if __name__ == "__main__":
    obj = EHentaiApi()
    print(obj.choose_fun(["111", "s", "Heartful mama"]))
