'''
pip3 install itchat

构建管道
'''
import itchat, time
from itchat.content import TEXT
import zmq
import threading


# 线程
def message_monitor():
    # recv scratch
    # quit_code = "quit!"
    rep_port = 38784
    rep_context = zmq.Context()
    rep_socket = rep_context.socket(zmq.REP)
    rep_socket.bind("tcp://*:%s" % rep_port)
    # get message from scratch
    while True:
        message = rep_socket.recv_json()
        username = message["username"]
        text = message["text"]
        rep_socket.send_json({"result": "get it!"})
        try:
            user2SendMessage = itchat.search_friends(nickName=username)[0]
            user2SendMessage.send(text)
        except:
            pass


bg_task = threading.Thread(target=message_monitor)
bg_task.daemon = True
bg_task.start()

port = 38783  # req 发送微信消息
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:%s" % port)


@itchat.msg_register([TEXT])
def text_reply(msg):
    # msg.user.send('%s: %s' % (msg.type, msg.text))
    # author = itchat.search_friends(nickName='Finn')[0]
    # author.send('hi ，我正通过codelab的Scratch界面与你聊天!')
    content = msg.text
    user = msg.user["NickName"]
    if content == "codelab":
        user.send("hi 感谢参与测试：）")
    socket.send_json({"username":user,"text":content})
    socket.recv_json().get("result")


itchat.auto_login(True)
itchat.run(True)
