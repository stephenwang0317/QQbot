import requests
from Baidu_Text_transAPI import translate


class TextApi:
    def __init__(self):
        self.proxies = {
            'http': None,
            'https': None
        }
        self.fun_map = {
            "求喷": self.get_rubbish,
            "求夸": self.getTuwei,
            "翻译": self.get_translate
        }
        self.instruct_list = list(self.fun_map.keys())

    def get_rubbish(self, param):
        url = 'https://act.jiawei.xin:10086/lib/api/maren.php?catalog=yang&format=json'
        headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }
        try:
            r = requests.get(url=url, timeout=5, proxies=self.proxies)
            newJson = r.json()
            return newJson['text']
        except Exception as e:
            return "超时"

    def getTuwei(self, param):
        url = 'https://api.1314.cool/words/api.php?return=json'
        headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }
        r = requests.get(url=url, proxies=self.proxies)
        newJson = r.json()
        str = newJson['word'].replace("<br>", "")
        return str

    def get_translate(self, param):
        if len(param) == 1:
            return "请输入翻译内容"
        ans = translate(param[1], proxies=self.proxies)
        return ans['trans_result'][0]['dst']

    def choose_fun(self, params: list) -> str:
        func = self.fun_map.get(params[0])
        return func(params)
