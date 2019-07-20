'''
zmq作为管道 req/rep
'''

import time
import zmq

from codelab_adapter.core_extension import Extension
from codelab_adapter import settings

# connect req
port = 38778
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect ("tcp://localhost:%s" % port)

class BlenderExtension(Extension):
    '''
    todo:
        实现json-rpc
    '''
    def __init__(self):
        name = type(self).__name__ # class name
        super().__init__(name)

    def run(self):
        while self._running:
            message = self.read()
            socket.send_json(message)
            print("send to blender server {}".format(message))
            result = socket.recv_json()
            print("result: {}".format(result))

export = BlenderExtension
