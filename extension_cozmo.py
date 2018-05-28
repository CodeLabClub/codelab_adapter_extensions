'''
把cozmo跑在一个端口上(视为外部硬件) zmq作为管道 req/rep
'''

import time
import zmq

from scratch3_adapter.core_extension import Extension
from scratch3_adapter import settings

# connect req
port = 38777
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect ("tcp://localhost:%s" % port)

class CozmoExtension(Extension):
    def __init__(self):
        name = type(self).__name__ # class name
        super().__init__(name)

    def run(self):
        while True:
            message = self.read()
            socket.send_json(message) # 设置超时
            print("send to cozmo server {}".format(message))
            result = socket.recv_json()
            print("result: {}".format(result))

export = CozmoExtension
