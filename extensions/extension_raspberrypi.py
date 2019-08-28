
'''
Raspberry Pi
requirement:
    pip3 install gpiozero pigpio --user
'''
import zmq
import subprocess
import pathlib
import platform

from codelab_adapter import settings
from codelab_adapter.core_extension import Extension

def get_python3_path():
    # If it is not working,  Please replace python3_path with your local python3 path. shell: which python3
    if (platform.system() == "Darwin"):
        # which python3
        # 不如用PATH python
        # 不确定
        path = "/usr/local/bin/python3"
    if platform.system() == "Windows":
        path = "python"
    if platform.system() == "Linux":
        path = "/usr/bin/python3"
    return path


python3_path = get_python3_path()

class RpiExtension(Extension):
    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)
        self.TOPIC = "eim/rpi"

    def run(self):
        # 抽象掉这部分 Class
        port = 38782 # todo 随机分配
        context = zmq.Context.instance()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:%s" % port)
        codelab_adapter_server_dir = pathlib.Path.home(
        ) / "codelab_adapter" / "servers"
        script = "{}/raspberrypi_server.py".format(codelab_adapter_server_dir)

        cmd = [python3_path, script]
        rpi_server = subprocess.Popen(cmd)
        settings.running_child_procs.append(rpi_server)

        while self._running:
            message = self.read()
            self.logger.debug(message)
            topic = message.get('topic')
            python_code = message.get("payload")
            if topic == self.TOPIC:
                socket.send_json({"python_code": python_code})
                result = socket.recv_json().get("result")
                # 发往scratch3.0
                self.publish({"topic": self.TOPIC, "payload": result})

        # release socket
        socket.send_json({"python_code": "quit!"})
        result = socket.recv_json().get("result")
        rpi_server.terminate()
        rpi_server.wait()
        socket.close()
        context.term()


export = RpiExtension