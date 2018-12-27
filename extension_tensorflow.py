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
        # 驱动外部进程
        # shell中的环境变量不见了
        cmd = "/usr/bin/python3 /home/pi/Object_detection_for_adapter.py"
        tf = subprocess.Popen(cmd , shell = True)
        while self._running:
            tf_class = socket.recv_json().get("class")
            self.logger.info("Received request: {message}".format(message=tf_class))
            self.publish({"topic": "eim", "message": tf_class})
            socket.send_json({"status":"200"})
        # release socket
        # 小心强行关闭
        # 还是无法kill
        tf.terminate()
        tf.wait()
        # ksubprocess.Popen.kill(tf)
        socket.close()
        context.term()

export = TensorflowExtension
