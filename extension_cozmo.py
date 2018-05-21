'''
把cozmo跑在一个端口上(视为外部硬件) zmq作为管道 req/rep

cozmo server在dev_example.py
'''

import time
import zmq

from scratch3_adapter.core_extension import Extension
from scratch3_adapter import settings

print("cozmo ok")


# 使用req
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
            if settings.DEBUG != 0:
                # pass
                self.logger.info("cozmo: {}".format(time.time()))
                time.sleep(1)
            '''
            message = {}
            # message["topic"] = "cozmo/sensor" # cozmo/actuator
            message["topic"] = "cozmo/actuator"
            message["data"] = "hello" # cozmo/actuator
            '''
            self.read()
            socket.send_json(self.message) # 设置超时
            print("send to cozmo server {}".format(self.message))
            # import Iython;IPython.embed()
            result = socket.recv_json()
            print("result: {}".format(result))

export = CozmoExtension
