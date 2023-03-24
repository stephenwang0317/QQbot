import os
import random


class VoiceApi:
    def __init__(self):
        self.func_map = {
            "塔菲": self.get_taffy_voice,
            "贝拉": self.get_bella_voice,
            "嘉然": self.get_diana_voice,
            "七海": self.get_nanami_voice,
            "东雪莲": self.get_hanjian_voice,
            "阿梓": self.get_azi_voice,
            "向晚": self.get_ava_voice
        }
        self.instruct_list = list(self.func_map.keys())


    def get_taffy_voice(self):
        list2 = os.listdir("../data/voices/taffy")
        filename = list2[random.randint(0, len(list2) - 1)]
        msg = '[CQ:record,file=./taffy/{}]'.format(filename)
        return msg

    def get_bella_voice(self):
        list2 = os.listdir("../data/voices/bella")
        filename = list2[random.randint(0, len(list2) - 1)]
        msg = '[CQ:record,file=./bella/{}]'.format(filename)
        return msg

    def get_diana_voice(self):
        list2 = os.listdir("../data/voices/diana")
        filename = list2[random.randint(0, len(list2) - 1)]
        msg = '[CQ:record,file=./diana/{}]'.format(filename)
        return msg

    def get_nanami_voice(self):
        list2 = os.listdir("../data/voices/nanami")
        filename = list2[random.randint(0, len(list2) - 1)]
        msg = '[CQ:record,file=./nanami/{}]'.format(filename)
        return msg

    def get_hanjian_voice(self):
        list2 = os.listdir("../data/voices/dongxuelian")
        filename = list2[random.randint(0, len(list2) - 1)]
        msg = '[CQ:record,file=./dongxuelian/{}]'.format(filename)
        return msg

    def get_azi_voice(self):
        list2 = os.listdir("../data/voices/azi")
        filename = list2[random.randint(0, len(list2) - 1)]
        msg = '[CQ:record,file=./azi/{}]'.format(filename)
        return msg

    def get_ava_voice(self):
        list2 = os.listdir("../data/voices/ava")
        filename = list2[random.randint(0, len(list2) - 1)]
        msg = '[CQ:record,file=./ava/{}]'.format(filename)
        return msg

    def choose_fun(self, params: list) -> str:
        func = self.func_map.get(params[0])
        return func()
