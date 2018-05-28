import time
import zmq

from scratch3_adapter.core_extension import Extension
from scratch3_adapter import settings

# connect req
port = 38778
context = zmq.Context()
socket = context.socket(zmq.REQ)
android_ip = "10.10.100.243"
socket.connect ("tcp://{}:{}".format(android_ip,port))

class CozmoExtension(Extension):
    def __init__(self):
        name = type(self).__name__ # class name
        super().__init__(name)

    def run(self):
        while True:
            message = self.read()
            socket.send_json(message) # 设置超时
            print("send to android server {}".format(message))
            result = socket.recv_json()
            print("result: {}".format(result))

export = CozmoExtension
