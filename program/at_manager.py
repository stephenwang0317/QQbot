import re
import requests


class AtManager:
    def __init__(self, qq_number, ):
        self.regex = r"\[CQ:at,qq={}\]".format(qq_number)
        self.img_regex = r"\[CQ:image,file=(.+),(.+),url=(.+)\]"

    def check_at(self, raw_msg):
        match_ans = re.findall(self.regex, raw_msg)
        return len(match_ans) > 0

    def check_reply(self, raw_msg):
        regex = r"\[CQ:reply,id=(-*\d+)\]"
        match_ans = re.findall(regex, raw_msg)
        if len(match_ans) > 0:
            return match_ans[0]
        else:
            return None

    def check_pic(self, raw_msg):
        match_ans = re.findall(self.img_regex, raw_msg)
        if len(match_ans) > 0:
            return match_ans[0][0]
        else:
            return None

    def __call__(self, raw_msg):

        if not self.check_at(raw_msg):
            return None
        print("check at true")

        reply_msg_id = self.check_reply(raw_msg)
        # reply msg
        if reply_msg_id is not None:
            print("check reply true: ", reply_msg_id)
            reply_msg = requests.get("http://127.0.0.1:5700/get_msg?message_id={}".format(reply_msg_id)).json()
            raw = reply_msg.get("data").get("message")

            file_id = self.check_pic(raw)
            if file_id is not None:
                print("check img true: ", file_id)
                img_info = requests.get("http://127.0.0.1:5700/get_image?file={}".format(file_id)).json()
                img_path = img_info.get("data").get("file")
                img_path = r"../" + img_path
                return img_path
