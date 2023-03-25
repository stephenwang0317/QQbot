import json
import os
import requests


class PictureApi:
    def __init__(self):
        self.fun_map = {
            "狗": self.get_dog,
            "鸭子": self.get_duck,
            "猫": self.get_cat,
            "狐狸": self.get_fox,
            "色图": self.get_setu
        }
        self.instruct_list = list(self.fun_map.keys())
        self.proxies = {
            'http': None,
            'https': None
        }

    def get_dog(self, param):
        url = 'https://dog.ceo/api/breeds/image/random'
        headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }
        r = requests.get(url=url, proxies=self.proxies)
        newJson = r.json()
        msg = ""
        if newJson['status'] == "success":
            msg = " [CQ:image,timeout=5,file={}]".format(newJson['message'])
        else:
            msg = "网络错误"
        return msg

    def get_duck(self, param):
        url = 'https://random-d.uk/api/v2/random'
        headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }
        r = requests.get(url=url, proxies=self.proxies)
        newJson = r.json()
        msg = ""
        msg = " [CQ:image,timeout=5,file={}]".format(newJson['url'])
        return msg

    def get_cat(self, param):
        url = 'https://api.thecatapi.com/v1/images/search?size=thumb'
        headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }
        r = requests.get(url=url, proxies=self.proxies)
        newJson = r.json()
        msg = ""
        msg = " [CQ:image,timeout=5,file={}]".format(newJson[0]['url'])
        return msg

    def get_fox(self, param):
        url = 'https://randomfox.ca/floof/'
        headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }
        r = requests.get(url=url, headers=headers, proxies=self.proxies)
        newJson = r.json()
        msg = ""
        msg = " [CQ:image,timeout=5,file={}]".format(newJson['image'])
        return msg

    def choose_fun(self, params: list) -> str:
        func = self.fun_map.get(params[0])
        return func(params)

    def get_setu(self, params):
        if len(params) == 1:
            tag = ""
        else:
            tag = params[1]

        data = {
            'r18': 1,
            'size': 'small',
            'tag': tag
        }
        url = 'https://api.lolicon.app/setu/v2'
        r = requests.get(url=url, params=data, proxies=self.proxies)
        ret = json.loads(r.text)['data']
        if len(ret) == 0:
            return "没查询到"

        ret = ret[0]
        msg = ""
        msg = msg + ret.get('title') + '\n'
        for item in ret.get('tags'):
            msg = msg + item + ','
        msg = msg + '\n'
        msg = msg + "[CQ:image,timeout=5,file={}]".format(ret.get('urls').get('small')) + '\n'
        return msg
