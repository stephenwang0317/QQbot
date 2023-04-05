from cgitb import html
import json
import os
import datetime
import threading
import time
import requests
import lxml
import random
import re
import schedule
import socket
from bs4 import BeautifulSoup
from Baidu_Text_transAPI import translate
from ehentai import EHentaiApi
from temp_file import Decoder
from send_msg import sendPrivateMessage, sendGroupMessage, send_msg, get_reply_msg
from vtuber_voice import VoiceApi
from get_picture import PictureApi
from get_text import TextApi
from javdb import JavDb
from at_manager import AtManager
from nsfw_predictor import NsfwPredictor

proxy2 = {
    'http': 'http://127.0.0.1:7890/',
    'https': 'http://127.0.0.1:7890/'
}


def decodeExp(exp):  # exp = raw_message
    tmp = exp.strip('#')
    str = tmp.split(" ", 1)
    if (len(str) == 1):
        str.append(" ")
    return {'exp': str[0], 'param': str[1]}


def checkCQCode(message):  # message = raw_message
    return re.search('^\[CQ:(.+?)\]', message)


def getCQCode(message):  # message = rwa_message
    return re.findall('^\[CQ:(.+?)[,\]]', message)[0]


def getCQParam(message):  # message = raw_message
    return re.findall('=(.+?)[,\]]', message)


def getCover(query):
    url = 'https://avmoo.click/cn/search/' + query  # 手动拼接
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    txt = ""
    i = 0
    while len(txt) == 0 and i < 20:
        try:
            r = requests.get(url=url, headers=headers, proxies=proxy2)
            txt = r.text
            # print(txt)
            r.close()
        except:
            print("error" + str(i))
        i += 1

    if len(txt) == 0:
        return "被反爬了"
    else:
        msg = ""
        bf = BeautifulSoup(txt, "lxml")
        item = bf.find("div", "photo-frame")
        print(item.find('img').get('title'))
        if item != None:
            msg = "查询条件 = {query}\n {title}\n [CQ:image,timeout=5,file={src}]".format(
                title=item.find('img').get('title'), src=item.find('img').get('src'), query=query)
        else:
            msg = "没找到"
        return msg


def getMagnet(tag):  # 返回组装好的msg
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.77',
        "cookie": 'challenge=4ca42f78fda437582e77b9f9a45c3376; ex=1'
    }
    url = 'https://clm8.in/search'
    data = {
        'word': tag
    }
    txt = ""
    i = 0
    while len(txt) == 0 and i < 10:
        try:
            r = requests.get(url=url, params=data, headers=headers)
            txt = r.text
            r.close()
        except:
            print(i)
        i += 1
    bf = BeautifulSoup(txt, 'lxml')
    list1 = bf.find_all("a", "SearchListTitle_result_title")  # search result
    subUrlPrefix = 'https://clm8.in'
    msg = ""
    i = 0
    for item in list1:
        if i > 5:
            break
        urlSuffix = item.get('href')
        url2 = subUrlPrefix + urlSuffix
        r2 = requests.get(url=url2, headers=headers)
        subBf = BeautifulSoup(r2.text, 'lxml')
        if subBf.find('h1', 'Information_title') != None:
            msg = msg + subBf.find('h1', 'Information_title').string + "\n" + subBf.find('a', 'Information_magnet').get(
                'href') + "\n\n"
        else:
            msg = "啥也没有"
        r2.close()
        i += 1
    if len(list1) == 0:
        msg = "啥也没有"

    return msg


def getReplyMsg(rev):
    return "[CQ:reply,id={id}][CQ:at,qq={qq}] ".format(id=rev['message_id'], qq=rev['user_id'])


def getActress(page):
    if page.isspace():
        page = "1"
    url = 'https://avmoo.click/cn/actresses/page/' + page
    i = 0
    txt = ""
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; '
                      'Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    }
    while len(txt) == 0 and i < 10:
        try:
            r = requests.get(url=url, headers=headers, proxies=proxy2)
            txt = r.text
            r.close()
        except:
            print(i)
            time.sleep(0.5)
        i += 1
    msg = ""
    bf = BeautifulSoup(txt, "lxml")
    list1 = bf.find_all("div", "photo-info")
    for item in list1:
        msg += item.find('span').string + "\n"
    if msg.isspace():
        msg = "被反爬"
    return msg


def checkAndGetPic(msg, tagList):
    print("checkAndGetPic")
    ret = ""
    for name in tagList:
        nameWithoutSuffix = re.findall("^(.+?)\.", name, flags=re.IGNORECASE)[0]
        # print(nameWithoutSuffix)
        if re.search(nameWithoutSuffix, msg) != None:
            filePath = "./pic/" + name
            ret = "[CQ:image,file={},subType=1]".format(filePath)
    print(ret)
    return ret


class Bot:
    def __init__(self):
        self.staticReply = [
            "别狗叫",
            "窝嫩爹",
            "急了？",
            "典",
            "典中典"
        ]

        print("STARTTTTTTTTTTTTTTTTTTTTTTTTTTT")

        self.fileNameList = os.listdir("../data/images/pic")
        self.wakeupList = os.listdir("../data/voices/wakeup")
        print(self.wakeupList)

        # 创建进程执行定时任务
        self.t1 = threading.Thread(target=self.scheduleWork)
        self.t1.start()

        self.bot_qqnumber = requests.get("http://127.0.0.1:5700/get_login_info").json().get('data').get('user_id')

        self.at_manager = AtManager(self.bot_qqnumber)
        self.nsfw = NsfwPredictor()

        self.ehantai = EHentaiApi()
        self.voice = VoiceApi()
        self.decoder = Decoder()
        self.picture = PictureApi()
        self.text = TextApi()
        self.javdb = JavDb()

    def sendWakeUp(self):
        now = datetime.datetime.now()
        print(now.day)
        sendGroupMessage(id="617092385", message="[CQ:record,file=./wakeup/{}]".format(self.wakeupList[(now.day) % 5]))

    def scheduleWork(self):
        schedule.every().day.at("08:00").do(self.sendWakeUp)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def __call__(self, rev):
        if rev is not None and rev['post_type'] == 'message':  # 消息
            print(rev)
            rawMessage = rev['raw_message']
            if rawMessage.startswith('#'):  # 指令
                params = self.decoder.process(rawMessage)
                deMessage = decodeExp(rawMessage)
                # 番号指令
                if deMessage['exp'] == '番号':
                    send_msg(rev, message=(self.javdb.choose_fun(params) + get_reply_msg(rev)))

                # 磁力指令
                elif deMessage['exp'] == '磁力':
                    send_msg(rev, message=getReplyMsg(rev) + getMagnet(deMessage['param']))

                # 老师指令
                elif deMessage['exp'] == '老师':
                    send_msg(rev, message=getReplyMsg(rev) + getActress(deMessage['param']))

                elif deMessage['exp'] in self.text.instruct_list:
                    print("text")
                    send_msg(rev, message=(self.text.choose_fun(params) + get_reply_msg(rev)))
                elif deMessage['exp'] in self.picture.instruct_list:
                    print("picture")
                    send_msg(rev, message=(self.picture.choose_fun(params) + get_reply_msg(rev)))
                elif deMessage['exp'] in self.voice.instruct_list:
                    send_msg(rev, self.voice.choose_fun(params))
                elif deMessage['exp'] == '本子':
                    send_msg(rev=rev, message=self.ehantai.choose_fun(params))
                # 未知指令
                else:
                    send_msg(rev=rev, message="听不懂")





            elif rev != None:  # 非指令
                ret_val = self.at_manager(rawMessage)

                result = self.nsfw.process(ret_val)
                send_msg(rev, message=result['class'])
                print("send_msg = " + result['class'])

                if rev['message_type'] == 'private':
                    msg = checkAndGetPic(rawMessage, self.fileNameList)
                    if (msg == ""):
                        print("here1")
                        sendPrivateMessage(id=rev['user_id'],
                                           message=self.staticReply[random.randint(0, len(self.staticReply) - 1)])
                    else:
                        print("here2")
                        sendPrivateMessage(id=rev['user_id'], message=msg)
                elif rev['message_type'] == 'group':
                    if (checkCQCode(rawMessage) and getCQCode(rawMessage) == 'at'):  # at
                        qqnumber = getCQParam(rawMessage)[0]
                        if (qqnumber == str(rev["self_id"])):  # at Bot
                            sendGroupMessage(id=rev['group_id'],
                                             message=self.staticReply[random.randint(0, len(self.staticReply) - 1)])
                        # elif re.search('^\[CQ:(.+?)\] 喷他', rawMessage) != None:
                        #     msg = "[CQ:at,qq={}] ".format(qqnumber)
                        #     msg = msg + getRubbish()
                        #     if qqnumber == "1600842796":
                        #         sendGroupMessage(id=rev['group_id'], message="不能喷主人")
                        #     else:
                        #         sendGroupMessage(id=rev['group_id'], message=msg)
                        # elif re.search('^\[CQ:(.+?)\] 轻喷', rawMessage) != None:
                        #     msg = "[CQ:at,qq={}] ".format(qqnumber)
                        #     msg = msg + getEasyRubbish()
                        #     if qqnumber == "1600842796":
                        #         sendGroupMessage(id=rev['group_id'], message="不能喷主人")
                        #     else:
                        #         sendGroupMessage(id=rev['group_id'], message=msg)
                    elif checkAndGetPic(rawMessage, self.fileNameList).isspace() == False:
                        sendGroupMessage(id=rev['group_id'], message=checkAndGetPic(rawMessage, self.fileNameList))
        elif rev is not None and rev['post_type'] == 'notice':
            if rev['notice_type'] == 'group_ban':
                if rev['sub_type'] == 'ban':
                    sendGroupMessage(id=rev['group_id'], message="好似喵 好似喵")
                elif rev['sub_type'] == 'lift_ban':
                    sendGroupMessage(id=rev['group_id'], message="好活喵 好活喵")
