import zmq
import subprocess
import pathlib
import platform

from codelab_adapter.core_extension import Extension
from codelab_adapter import settings


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


class VectorExtension(Extension):
    def __init__(self):
        name = type(self).__name__
        super().__init__(name)
        self.TOPIC = "eim/vector"  # eim + [extension id]

    def run(self):

        port = 38781
        context = zmq.Context.instance()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:%s" % port)
        codelab_adapter_server_dir = pathlib.Path.home(
        ) / "codelab_adapter" / "servers"
        script = "{}/vector_server.py".format(codelab_adapter_server_dir)

        cmd = [python3_path, script]
        vector_server = subprocess.Popen(cmd)
        settings.running_child_procs.append(vector_server)

        while self._running:
            message = self.read()  # 有可能有阻塞在这里，关掉插件后，还需要scratch3发一条消息。
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
        vector_server.terminate()
        vector_server.wait()
        socket.close()
        context.term()


export = VectorExtension
