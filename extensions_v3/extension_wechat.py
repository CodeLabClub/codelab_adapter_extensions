'''
todo
    自动登陆默认不启用，可通过配置项启用
    kill itchat thread
'''

import zmq
import pathlib
import threading
from codelab_adapter.utils import threaded, is_win
from codelab_adapter.core_extension import Extension

if is_win():
    import io
    from contextlib import redirect_stdout, redirect_stderr
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        import itchat, time
        from itchat.content import TEXT
else:
    import itchat, time
    from itchat.content import TEXT


codelab_adapter_dir = pathlib.Path.home() / "codelab_adapter"

class WechatGateway(Extension):

    NODE_ID = "eim/extension_wechat"
    HELP_URL = "https://adapter.codelab.club/extension_guide/wechat/"
    DESCRIPTION = "将微信积木化" # wechat -- 勉强能用的聊天工具

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def extension_message_handle(self, topic, payload):
        '''
        使用scratch发送微信消息
        '''
        self.logger.debug(f"wechat message {payload['content']}")
        username = payload["username"]
        text = payload["content"]
        type = payload.get("type")
        try:
            if type == 'group':
                user2SendMessage = itchat.search_chatrooms(username)[0]
            if type == 'user':
                user2SendMessage = itchat.search_friends(nickName=username)[0]
            user2SendMessage.send(text)
        except Exception as e:
            self.logger.error(str(e))

    def run(self):
        self.wechat_run_as_thread()
        while self._running:
            time.sleep(1)

    # 用户消息
    def text_reply(self, msg):
        '''
        来自微信的消息，发往Scratch
        '''
        # msg.user.send('%s: %s' % (msg.type, msg.text))
        # author = itchat.search_friends(nickName='Finn')[0]
        # author.send('hi ，我正通过codelab的Scratch界面与你聊天!')
        self.logger.info(str(msg))
        # return 文件助手会错误
        content = msg.text
        username = msg.user["NickName"]
        # if content == "codelab":
        #     user.send("hi 感谢参与测试：）")
        try:
            message = {}
            message["payload"] = {}
            message["payload"] = {
                "username": username,
                "content": content,
            }
            self.publish(message)
        except Exception as e:
            self.logger.error(str(e))

    # 群消息
    def group_text_reply(self, msg):
        '''
        将群消息发往scratch
        '''

        content = msg.text
        username = msg.actualNickName
        try:
            # 群消息有时候会有问题 msg.User.NickName不存在
            group_name = msg.User.NickName
        except:
            return
        try:
            # groupname: 群消息
            message = {}
            message["payload"] = {
                "username": username,
                "content": content,
                "groupname": group_name
            }
            self.publish(message)
        except Exception as e:
            self.logger.error(str(e))

    @threaded
    def wechat_run_as_thread(self):
        # todo kill itchat
        picDir = str(codelab_adapter_dir / "extensions" /
                     "adapter_QR.png")  # fix 打包软件打开本地图片的权限问题
        statusStorageDir = str(
            codelab_adapter_dir / "extensions" / 'adapter_itchat.pkl')
        itchat.msg_register([TEXT])(self.text_reply)
        itchat.msg_register(TEXT, isGroupChat=True)(self.group_text_reply)
        itchat.auto_login(
            True, picDir=picDir, statusStorageDir=statusStorageDir)
        itchat.run(True)  # todo 提示有些账号无法登录


export = WechatGateway

if __name__ == "__main__":
    w = WechatGateway()
    threaded(w.receive_loop)()
    w.run()