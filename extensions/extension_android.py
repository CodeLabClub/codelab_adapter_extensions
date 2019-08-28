import time, threading
import zmq

from codelab_adapter.core_extension import Extension
from codelab_adapter import settings

# todo 这个插件可以做成通用的，连接有scratch3决定

# connect req
android_ip = "10.10.100.243"
port = 38778
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://{}:{}".format(android_ip,port))

# ip在一处配置，让REQ来bind
port_sensor = 38779
context_sonsor = zmq.Context()
socket_sonsor = context_sonsor.socket(zmq.REP)
socket_sonsor.connect("tcp://{}:{}".format(android_ip,port_sensor))


class AndroidExtension(Extension):
    def __init__(self):
        name = type(self).__name__ # class name
        super().__init__(name)

    def bg_task(self):
        while True:
            # recv
            message = socket_sonsor.recv_json()
            # print(message)
            time.sleep(1)
            self.logger.info("sensor pipe recv: %s", message)
            # pub 到scratch3
            self.publish({"topic":"sensor/android","payload":message})
            socket_sonsor.send_json({"result":"ok"})
        # 等待android的数据，推到scratch3
        # 写一个安卓的 scratch3插件
        # self.publish({})

    def run(self):
        bg_thread = threading.Thread(target = self.bg_task)
        self.logger.info("thread start")
        bg_thread.daemon = True
        bg_thread.start()

        while True:
            # send then recv
            message = self.read()
            socket.send_json(message) # 设置超时
            print("send to android server {}".format(message))
            result = socket.recv_json()
            print("result: {}".format(result))

export = AndroidExtension
