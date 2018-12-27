import time
import zmq
from zmq import Context
import subprocess

from scratch3_adapter.core_extension import Extension
from scratch3_adapter import settings


class TensorflowExtension(Extension):
    def __init__(self):
        name = type(self).__name__ # class name
        super().__init__(name)

    def run(self):
        # REP
        port = 38779
        context = Context.instance()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:%s" % port)
        # Object_detection_for_adapter.py 依赖于shell中的变量，所以需要在命令行里启动
        cmd = "/usr/bin/python3 /home/pi/Object_detection_for_adapter.py"
        tf = subprocess.Popen(cmd , shell = True)
        while self._running:
            tf_class = socket.recv_json().get("class")
            socket.send_json({"status":"200"})
            # 发往scratch3.0中的eim积木
            self.publish({"topic": "eim", "message": tf_class})
        # release socket
        tf.terminate()
        tf.wait()
        socket.close()
        context.term()

export = TensorflowExtension
