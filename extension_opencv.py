# 文档: https://blog.just4fun.site/adapter-opencv.html
# 树莓派和macOS已测试
import time
import zmq
from zmq import Context
import subprocess
import pathlib
import platform

from codelab_adapter.core_extension import Extension
from codelab_adapter import settings


class OpencvExtension(Extension):
    def __init__(self):
        name = type(self).__name__ # class name
        super().__init__(name)

    def run(self):
        # REP
        port = 38780
        context = Context.instance()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:%s" % port)
        # Object_detection_for_adapter.py 依赖于shell中的变量，所以需要在命令行里启动
        # ~/codelab_adapter目录
        codelab_adapter_dir = pathlib.Path.home() / "codelab_adapter"
        script =  "{}/ExploreOpencvDnn/main_for_adapter.py".format(codelab_adapter_dir)
        if (platform.system() == "Darwin"):
            # which python3
            python = "/usr/local/bin/python3"
        if platform.system() == "Windows":
            python = "python"
        if platform.system() == "Linux":
            python = "/usr/bin/python3"
        cmd = [python, script]
        tf = subprocess.Popen(cmd)
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

export = OpencvExtension
