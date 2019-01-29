import sys
sys.path.append("/usr/local/lib/python3.6/site-packages")

import time
import threading

from codelab_adapter import settings
from codelab_adapter.core_extension import Extension

import itchat, time
from itchat.content import *

global scratch_message_queue
scratch_message_queue = []
global wechat_message_queue
wechat_message_queue = []

global author
author = 0


@itchat.msg_register([TEXT])
def text_reply(msg):
    global author
    # 用户发送信息过来, 存到队列里
    # msg.user.send('%s: %s' % (msg.type, msg.text))
    # author = itchat.search_friends(nickName='Finn')[0]
    # author.send('hi ，我正通过codelab的Scratch界面与你聊天!')
    if msg.text == "codelab":
        author = msg.user  # todo: 只处理某个用户
        author.send("hi 感谢参与测试：）")
    content = msg.text
    wechat_message_queue.append(content)


def message_queue_monitor():
    global scratch_message_queue
    global author
    if scratch_message_queue:
        for i in scratch_message_queue:
            current_message = i
            print("scratch current_message: ", current_message)
            author.send(current_message)
            scratch_message_queue.remove(current_message)
            time.sleep(1)


# 检查是否发送
message4wechat_task = threading.Thread(target=message_queue_monitor)
message4wechat_task.daemon = True
message4wechat_task.start()
'''
使用scratch作为微信聊天界面
    扫码登陆
    聊天框
    两个人
        说话 + 文字

    消息发往微信 和 微信过来的消息，不需要uuid

使用双向消息模拟出request-response

# 使用一个全局变量处理消息 是否应答 dict 消息 ID(uuid)
# 构建队列 标识是否被处理
消息格式{}
    消息id + 消息体
    uuid:{"is_completed":true/false,"content":"hi","type":"request/response"}
    消息对
两边不一样
'''


class WechatExtension(Extension):
    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)

    def run(self):
        '''
        run 会被作为线程调用
        当前插件功能:
            往scratch不断发送信息
        '''

        def message_monitor():
            global scratch_message_queue, author
            while True:
                read_message = self.read()  # json
                self.logger.debug("message:%s", str(read_message))
                data = read_message["data"]
                if read_message.get("topic") == "eim":
                    author.send(data)
                    # scratch_message_queue.append(data)

        bg_task = threading.Thread(target=message_monitor)
        self.logger.info("thread start")
        bg_task.daemon = True
        bg_task.start()

        while self._running:
            if settings.DEBUG:
                if wechat_message_queue:
                    for c_message in wechat_message_queue:
                        current_message = c_message
                        message = {"topic": "eim", "message": current_message}
                        self.publish(message)
                        wechat_message_queue.remove(current_message)
                        time.sleep(1)


export = WechatExtension


# 检查是否发送
def run_wechat():
    itchat.auto_login(True)
    itchat.run(True)


# 不要阻塞adapter
message4wechat_task = threading.Thread(target=run_wechat)
message4wechat_task.daemon = True
message4wechat_task.start()
