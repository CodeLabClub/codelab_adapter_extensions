'''
把cozmo跑在一个端口上(视为外部硬件) zmq作为管道 req/rep
'''

import time
import zmq
import platform
from codelab_adapter.core_extension import Extension
from codelab_adapter import settings
import pathlib
import subprocess

def get_python3_path():
    # If it is not working,  Please replace python3_path with your local python3 path. shell: which python3
    if (platform.system() == "Darwin"):
        # which python3
        path = "/usr/local/bin/python3"
    if platform.system() == "Windows":
        path = "python"
    if platform.system() == "Linux":
        path = "/usr/bin/python3"
    return path


python3_path = get_python3_path()


class CozmoExtension(Extension):
    '''
    todo:
        实现json-rpc
    '''

    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)
        self.TOPIC = "eim/cozmo"  # eim + [extension id]

    def run(self):
        # connect req
        port = 38777
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:%s" % port)
        codelab_adapter_server_dir = pathlib.Path.home(
        ) / "codelab_adapter" / "servers"
        script = "{}/cozmo_server.py".format(codelab_adapter_server_dir)
        cmd = [python3_path, script]
        cozmo_server = subprocess.Popen(cmd)
        settings.running_child_procs.append(cozmo_server)

        while self._running:
            message = self.read()
            self.logger.debug(message)
            topic = message.get('topic')
            python_code = message.get("payload")
            if topic == self.TOPIC:
                socket.send_json({"python_code": python_code})
                # socket.send_json(message) # 设置超时
                result = socket.recv_json().get("result")
                # 发往scratch3.0
                self.publish({"topic": self.TOPIC, "payload": result})

        # release socket
        socket.send_json({"python_code": "quit!"})
        result = socket.recv_json().get("result")
        cozmo_server.terminate()
        cozmo_server.wait()
        socket.close()
        context.term()


export = CozmoExtension