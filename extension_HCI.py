'''
HCI: human–machine interaction
本插件支持将任何输入映射为鼠标键盘行为

requirement:
    pip3 install pyautogui --user

todo:
    在Scratch3.0中写一个能自己写程序的程序
'''

import zmq
import subprocess
import pathlib
import platform

from codelab_adapter import settings
from codelab_adapter.core_extension import Extension

def get_python3_path():
    # todo: move to utils
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

class HCIExtension(Extension):
    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)
        self.TOPIC = "eim/HCI"

    def run(self):

        port = 38782
        context = zmq.Context.instance()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:%s" % port)
        codelab_adapter_server_dir = pathlib.Path.home(
        ) / "codelab_adapter" / "servers"
        script = "{}/HCI_server.py".format(codelab_adapter_server_dir)

        cmd = [python3_path, script]
        rpi_server = subprocess.Popen(cmd)
        settings.running_child_procs.append(rpi_server)

        while self._running:
            message = self.read()
            self.logger.debug(message)
            topic = message.get('topic')
            python_code = message.get('data')
            if topic == self.TOPIC:
                socket.send_json({"python_code": python_code})
                result = socket.recv_json().get("result")
                # 发往scratch3.0
                self.publish({"topic": self.TOPIC, "message": result})

        # release socket
        socket.send_json({"python_code": "quit!"})
        result = socket.recv_json().get("result")
        rpi_server.terminate()
        rpi_server.wait()
        socket.close()
        context.term()


export = HCIExtension