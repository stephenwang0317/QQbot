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
from receive import rev_msg
from Baidu_Text_transAPI import translate
from ehentai import EHentaiApi

def sendPrivateMessage(id,message):
    #print("id = "+ str(id))
    #print("msg = "+message)
    data = {
        'user_id':id,
        'message':message,
        'auto_escape':False
    }
    api_url = 'http://127.0.0.1:5700/send_private_msg'
    r = requests.post(api_url,data=data)
    print("r = "+ r.text)

def sendGroupMessage(id,message):
    data = {
        'group_id':id,
        'message':message,
        'auto_escape':False
    }
    api_url = 'http://127.0.0.1:5700/send_group_msg'
    r = requests.post(api_url,data=data)


def decodeExp(exp): # exp = raw_message
    tmp = exp.strip('/')
    str = tmp.split(" ",1)
    if(len(str) == 1):
        str.append(" ")
    return {'exp':str[0],'param':str[1]} 

def checkCQCode(message):   # message = raw_message
    return re.search('^\[CQ:(.+?)\]',message)

def getCQCode(message):  # message = rwa_message
    return re.findall('^\[CQ:(.+?)[,\]]',message)[0]

def getCQParam(message):     # message = raw_message
    return re.findall('=(.+?)[,\]]',message)

def getSetu(tag,flag):
    data = {
        'r18':flag,
        'size':'small',
        'tag':tag
    }
    url = 'https://api.lolicon.app/setu/v2'
    r = requests.get(url=url,params=data)
    print(r.text)
    return r

def getCover(query):
    url = 'https://avmoo.click/cn/search/' + query    #手动拼接
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    txt = ""
    i = 0 
    while len(txt) == 0 and i<20 :
        try:
            r = requests.get(url=url, headers=headers)
            txt = r.text
            #print(txt)
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
        if item != None :
            msg = "查询条件 = {query}\n {title}\n [CQ:image,timeout=5,file={src}]".format(title=item.find('img').get('title'), src=item.find('img').get('src'),query=query)
        else:
            msg = "没找到"
        return msg

def getMagnet(tag):     # 返回组装好的msg
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
    while len(txt) == 0 and i<10:
        try:
            r = requests.get(url=url, params=data, headers=headers)
            txt = r.text
            r.close()
        except:
            print(i)
        i += 1
    bf = BeautifulSoup(txt,'lxml')
    list1 = bf.find_all("a", "SearchListTitle_result_title")    #search result
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
        if subBf.find('h1','Information_title') != None:
            msg = msg + subBf.find('h1','Information_title').string + "\n" + subBf.find('a', 'Information_magnet').get('href') + "\n\n"
        else:
            msg = "啥也没有"
        r2.close()
        i += 1
    if len(list1) == 0:
        msg = "啥也没有"

    return msg

def getReplyMsg(rev):
    return "[CQ:reply,id={id}][CQ:at,qq={qq}] ".format(id=rev['message_id'],qq=rev['user_id'])

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
    while len(txt) == 0 and i<10:
        try:
            r = requests.get(url=url, headers=headers)
            txt = r.text
            r.close()
        except:
            print(i)
            time.sleep(0.5)
        i += 1
    msg = ""
    bf = BeautifulSoup(txt,"lxml")
    list1 = bf.find_all("div", "photo-info")
    for item in list1:
        msg += item.find('span').string + "\n"
    if msg.isspace():
        msg = "被反爬"
    return msg

def getRubbish():
    url = 'https://act.jiawei.xin:10086/lib/api/maren.php?catalog=yang&format=json'
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    try:
        r = requests.get(url=url, timeout=5)
        newJson = r.json()
        return newJson['text']
    except Exception as e:
        return "超时"

def getEasyRubbish():
    url = 'https://act.jiawei.xin:10086/lib/api/maren.php?catalog=qiu&format=json'
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    try:
        r = requests.get(url=url)
        newJson = r.json()
        return newJson['text']
    except Exception as e:
        return "超时"
        
def getTuwei():
    url = 'https://api.1314.cool/words/api.php?return=json'
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    r = requests.get(url=url)
    newJson = r.json()
    str =  newJson['word'].replace("<br>","")
    return str

def getDog():
    url = 'https://dog.ceo/api/breeds/image/random'
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    r = requests.get(url=url)
    newJson = r.json()
    msg = ""
    if newJson['status'] == "success":
        msg = " [CQ:image,timeout=5,file={}]".format(newJson['message'])
    else:
        msg = "网络错误"
    return msg

def getDuck():
    url = 'https://random-d.uk/api/v2/random'
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    r = requests.get(url=url)
    newJson = r.json()
    msg = ""
    msg = " [CQ:image,timeout=5,file={}]".format(newJson['url'])
    return msg

def getCat():
    url = 'https://api.thecatapi.com/v1/images/search?size=thumb'
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    r = requests.get(url=url)
    newJson = r.json()
    msg = ""
    msg = " [CQ:image,timeout=5,file={}]".format(newJson[0]['url'])
    return msg

def getFox():
    url = 'https://randomfox.ca/floof/'
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    r = requests.get(url=url, headers=headers)
    newJson = r.json()
    msg = ""
    msg = " [CQ:image,timeout=5,file={}]".format(newJson['image'])
    return msg

def checkAndGetPic(msg,tagList):
    print("checkAndGetPic")
    ret = ""
    for name in tagList:
        nameWithoutSuffix = re.findall("^(.+?)\.",name,flags=re.IGNORECASE)[0]
        # print(nameWithoutSuffix)
        if re.search(nameWithoutSuffix,msg) != None:
            filePath = "./pic/" + name
            ret = "[CQ:image,file={},subType=1]".format(filePath)
    print(ret)
    return ret

def getTaffyVoice():
    list2 = os.listdir("../data/voices/taffy")
    filename = list2[random.randint(0,len(list2)-1)]
    msg = '[CQ:record,file=./taffy/{}]'.format(filename)
    return msg

def getBellaVoice():
    list2 = os.listdir("../data/voices/bella")
    filename = list2[random.randint(0,len(list2)-1)]
    msg = '[CQ:record,file=./bella/{}]'.format(filename)
    return msg

def getDianaVoice():
    list2 = os.listdir("../data/voices/diana")
    filename = list2[random.randint(0,len(list2)-1)]
    msg = '[CQ:record,file=./diana/{}]'.format(filename)
    return msg

def getNanamiVoice():
    list2 = os.listdir("../data/voices/nanami")
    filename = list2[random.randint(0,len(list2)-1)]
    msg = '[CQ:record,file=./nanami/{}]'.format(filename)
    return msg

def getHanjianVoice():
    list2 = os.listdir("../data/voices/dongxuelian")
    filename = list2[random.randint(0,len(list2)-1)]
    msg = '[CQ:record,file=./dongxuelian/{}]'.format(filename)
    return msg

def getAziVoice():
    list2 = os.listdir("../data/voices/azi")
    filename = list2[random.randint(0,len(list2)-1)]
    msg = '[CQ:record,file=./azi/{}]'.format(filename)
    return msg
def getAvaVoice():
    list2 = os.listdir("../data/voices/ava")
    filename = list2[random.randint(0,len(list2)-1)]
    msg = '[CQ:record,file=./ava/{}]'.format(filename)
    return msg

def sendWakeUp():
    now = datetime.datetime.now()
    print(now.day)
    sendGroupMessage(id="617092385", message="[CQ:record,file=./wakeup/{}]".format(wakeupList[(now.day)%5]))

def scheduleWork():
    schedule.every().day.at("08:00").do(sendWakeUp)
    while True:
        schedule.run_pending()
        time.sleep(1)


staticReply = [
    "别狗叫",
    "窝嫩爹",
    "急了？",
    "典",
    "典中典"
    ]

print("STARTTTTTTTTTTTTTTTTTTTTTTTTTTT")

fileNameList = os.listdir("../data/images/pic")
wakeupList = os.listdir("../data/voices/wakeup")
print(wakeupList)

#创建进程执行定时任务
t1 = threading.Thread(target=scheduleWork)
t1.start()

obj = EHentaiApi()

while True:
    rev = rev_msg()
    print("rev = ",end="")
    print(rev)
    if rev != None and rev['post_type'] == 'message':   #消息
        rawMessage = rev['raw_message']
        if rawMessage.startswith('/'):  #指令
           
            deMessage = decodeExp(rawMessage)
            #番号指令
            if deMessage['exp'] == '番号':
                msg = getReplyMsg(rev)
                msg += getCover(deMessage['param'])
                if rev['message_type'] == 'private':
                    sendPrivateMessage(
                        id = rev['user_id'],
                        message = msg
                    )
                elif rev['message_type'] == 'group':
                    sendGroupMessage(
                        id = rev['group_id'],
                        message = msg
                    )
            
            #色图指令   /色图
            elif deMessage['exp'] == '来点色图' or deMessage['exp'] == '色图':
                retVal = json.loads(getSetu(deMessage['param'],1).text)
                if(len(retVal['data']) == 0):   # 没查询到
                    src = "http://rcbqb.ccmeng.com:66/tp/dt/cqwm4bnprm1.jpg"
                else: 
                    src = retVal['data'][0]['urls']['small']
                if rev['message_type'] == 'private':
                    sendPrivateMessage(
                        id = rev['user_id'],
                        message = '[CQ:image,file={}]'.format(src)
                    )
                elif rev['message_type'] == 'group':
                    sendGroupMessage(
                        id = rev['group_id'],
                        message = '[CQ:image,file={}]'.format(src)
                    )

            #翻译指令
            elif deMessage['exp'] == '翻译':
                ans = translate(deMessage['param'])
                msg = getReplyMsg(rev) + ans['trans_result'][0]['dst']
                if rev['message_type'] == 'private':
                    sendPrivateMessage(id=rev['user_id'],message=msg)
                elif rev['message_type'] == 'group':
                    sendGroupMessage(id=rev['group_id'],message=msg)
            
            #磁力指令
            elif deMessage['exp'] == '磁力':
                if rev['message_type'] == 'private':
                    sendPrivateMessage(id=rev['user_id'],message=getReplyMsg(rev) + getMagnet(deMessage['param']))
                elif rev['message_type'] == 'group':
                    sendGroupMessage(id=rev['group_id'],message=getReplyMsg(rev) + getMagnet(deMessage['param']))

            #老师指令
            elif deMessage['exp'] == '老师':
                if rev['message_type'] == 'private':
                    sendPrivateMessage(id=rev['user_id'],message=getReplyMsg(rev) + getActress(deMessage['param']))
                elif rev['message_type'] == 'group':
                    sendGroupMessage(id=rev['group_id'],message=getReplyMsg(rev) + getActress(deMessage['param']))
            #求喷指令
            elif deMessage['exp'] == '求喷':
                if rev['message_type'] == 'private':
                    sendPrivateMessage(id=rev['user_id'],message=getReplyMsg(rev) + getRubbish())
                elif rev['message_type'] == 'group':
                    sendGroupMessage(id=rev['group_id'],message=getReplyMsg(rev) + getRubbish())
            #求夸指令
            elif deMessage['exp'] == '求夸':
                if rev['message_type'] == 'private':
                    sendPrivateMessage(id=rev['user_id'],message=getReplyMsg(rev) + getTuwei())
                elif rev['message_type'] == 'group':
                    sendGroupMessage(id=rev['group_id'],message=getReplyMsg(rev) + getTuwei())
            #狗指令
            elif deMessage['exp'] == '狗':
                if rev['message_type'] == 'private':
                    sendPrivateMessage(id=rev['user_id'],message=getReplyMsg(rev) + getDog())
                elif rev['message_type'] == 'group':
                    sendGroupMessage(id=rev['group_id'],message=getReplyMsg(rev) + getDog())
            #鸭指令
            elif deMessage['exp'] == '鸭子':
                if rev['message_type'] == 'private':
                    sendPrivateMessage(id=rev['user_id'],message=getReplyMsg(rev) + getDuck())
                elif rev['message_type'] == 'group':
                    sendGroupMessage(id=rev['group_id'],message=getReplyMsg(rev) + getDuck())
            #猫
            elif deMessage['exp'] == '猫':
                if rev['message_type'] == 'private':
                    sendPrivateMessage(id=rev['user_id'],message=getReplyMsg(rev) + getCat())
                elif rev['message_type'] == 'group':
                    sendGroupMessage(id=rev['group_id'],message=getReplyMsg(rev) + getCat())
            #狐狸指令
            elif deMessage['exp'] == '狐狸':
                if rev['message_type'] == 'private':
                    sendPrivateMessage(id=rev['user_id'],message=getReplyMsg(rev) + getFox())
                elif rev['message_type'] == 'group':
                    sendGroupMessage(id=rev['group_id'],message=getReplyMsg(rev) + getFox())
            #塔菲指令
            elif deMessage['exp'] == '塔菲':
                if rev['message_type'] == 'private':
                    sendPrivateMessage(id=rev['user_id'],message=getTaffyVoice())
                elif rev['message_type'] == 'group':
                    sendGroupMessage(id=rev['group_id'],message=getTaffyVoice())
            #贝拉指令
            elif deMessage['exp'] == '贝拉':
                if rev['message_type'] == 'private':
                    sendPrivateMessage(id=rev['user_id'],message=getBellaVoice())
                elif rev['message_type'] == 'group':
                    sendGroupMessage(id=rev['group_id'],message=getBellaVoice())
            elif deMessage['exp'] == '嘉然':
                if rev['message_type'] == 'private':
                    sendPrivateMessage(id=rev['user_id'],message=getDianaVoice())
                elif rev['message_type'] == 'group':
                    sendGroupMessage(id=rev['group_id'],message=getDianaVoice())
            elif deMessage['exp'] == '七海':
                if rev['message_type'] == 'private':
                    sendPrivateMessage(id=rev['user_id'],message=getNanamiVoice())
                elif rev['message_type'] == 'group':
                    sendGroupMessage(id=rev['group_id'],message=getNanamiVoice())
            elif deMessage['exp'] == '东雪莲':
                if rev['message_type'] == 'private':
                    sendPrivateMessage(id=rev['user_id'],message=getHanjianVoice())
                elif rev['message_type'] == 'group':
                    sendGroupMessage(id=rev['group_id'],message=getHanjianVoice())
            elif deMessage['exp'] == '阿梓':
                if rev['message_type'] == 'private':
                    sendPrivateMessage(id=rev['user_id'],message=getAziVoice())
                elif rev['message_type'] == 'group':
                    sendGroupMessage(id=rev['group_id'],message=getAziVoice())
            elif deMessage['exp'] == '向晚':
                if rev['message_type'] == 'private':
                    sendPrivateMessage(id=rev['user_id'],message=getAvaVoice())
                elif rev['message_type'] == 'group':
                    sendGroupMessage(id=rev['group_id'],message=getAvaVoice())
            elif deMessage['exp'] == '本子':
                if rev['message_type'] == 'private':
                    sendPrivateMessage(id=rev['user_id'],message=obj.generate_msg(obj.search(deMessage['param'])))
                elif rev['message_type'] == 'group':
                    sendGroupMessage(id=rev['group_id'],message=obj.generate_msg(obj.search(deMessage['param'])))

            #未知指令
            else:
                if rev['message_type'] == 'private':
                    sendPrivateMessage(id=rev['user_id'],message="听不懂")
                elif rev['message_type'] == 'group':
                    sendGroupMessage(id=rev['group_id'],message="听不懂")
        elif rev != None:   #非指令
            if rev['message_type'] == 'private':
                msg = checkAndGetPic(rawMessage,fileNameList)
                if(msg == ""):
                    print("here1")
                    sendPrivateMessage(id=rev['user_id'],message=staticReply[random.randint(0,len(staticReply)-1)])
                else:
                    print("here2")
                    sendPrivateMessage(id=rev['user_id'],message=msg)
            elif rev['message_type'] == 'group':
                if(checkCQCode(rawMessage) and getCQCode(rawMessage) == 'at'):  #at
                    qqnumber = getCQParam(rawMessage)[0]    
                    if(qqnumber == str(rev["self_id"])):  #at Bot
                        sendGroupMessage(id=rev['group_id'],message=staticReply[random.randint(0,len(staticReply)-1)])
                    elif re.search('^\[CQ:(.+?)\] 喷他',rawMessage) != None:
                        msg = "[CQ:at,qq={}] ".format(qqnumber)
                        msg = msg + getRubbish()
                        if qqnumber == "1600842796":
                            sendGroupMessage(id = rev['group_id'],message="不能喷主人")
                        else:    
                            sendGroupMessage(id = rev['group_id'],message=msg)
                    elif re.search('^\[CQ:(.+?)\] 轻喷',rawMessage) != None:
                        msg = "[CQ:at,qq={}] ".format(qqnumber)
                        msg = msg + getEasyRubbish()
                        if qqnumber == "1600842796":
                            sendGroupMessage(id = rev['group_id'],message="不能喷主人")
                        else:    
                            sendGroupMessage(id = rev['group_id'],message=msg)
                elif checkAndGetPic(rawMessage,fileNameList).isspace() == False:
                    sendGroupMessage(id=rev['group_id'],message=checkAndGetPic(rawMessage,fileNameList))
    elif rev !=None and rev['post_type'] == 'notice':
        if rev['notice_type'] == 'group_ban':
            if rev['sub_type'] == 'ban':
                sendGroupMessage(id=rev['group_id'], message="好似喵 好似喵")
            elif rev['sub_type'] == 'lift_ban':
                sendGroupMessage(id=rev['group_id'], message="好活喵 好活喵")
