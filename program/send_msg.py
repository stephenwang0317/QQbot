import requests


def sendPrivateMessage(id, message):
    # print("id = "+ str(id))
    # print("msg = "+message)
    data = {
        'user_id': id,
        'message': message,
        'auto_escape': False
    }
    api_url = 'http://127.0.0.1:5700/send_private_msg'
    r = requests.post(api_url, data=data)
    print("r = " + r.text)


def sendGroupMessage(id, message):
    data = {
        'group_id': id,
        'message': message,
        'auto_escape': False
    }
    api_url = 'http://127.0.0.1:5700/send_group_msg'
    r = requests.post(api_url, data=data)


def send_msg(rev, message):
    if rev['message_type'] == 'private':
        sendPrivateMessage(id=rev['user_id'], message=message)
    elif rev['message_type'] == 'group':
        sendGroupMessage(id=rev['group_id'], message=message)
