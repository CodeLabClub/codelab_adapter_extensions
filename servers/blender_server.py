# pip3 install pyzmq # blender
import zmq
import threading
from threading import Thread
from io import StringIO
import contextlib
import bpy
import sys
import logging
logger = logging.getLogger(__name__)

class BlenderServer(Thread):
    def __init__(self):
        super().__init__()
        self.port = 38785
        self.context = zmq.Context()
        self.is_running = True

    @contextlib.contextmanager
    def stdoutIO(self, stdout=None):
        old = sys.stdout
        if stdout is None:
            stdout = StringIO()
        sys.stdout = stdout
        yield stdout
        sys.stdout = old

    def run(self):
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s" % self.port)
        # cube = bpy.data.objects["Cube"]
        # cube.location.x += 0.2
        # bpy.data.objects["Cube"].location.x += 0.2
        while self.is_running:
            python_code = self.socket.recv_json().get("payload")
            print(python_code)
            logging
            try:
                with self.stdoutIO() as s:
                    exec(python_code)
                output = s.getvalue()
            except Exception as e:
                output = str(e)
            self.socket.send_json({"output": str(output).rstrip()})

    def terminate(self):
        # self.socket.close()
        self.is_running = False


server = BlenderServer()
server.setDaemon(True)
server.start()
