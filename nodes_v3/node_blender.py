# pip3 install codelab_adapter_client # blender
'''
运行在 blender 环境下
'''
from io import StringIO
import contextlib
import sys
import time

from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import threaded
import bpy # 
from loguru import logger


class BlenderNode(AdapterNode):
    def __init__(self):
        super().__init__()
        self.NODE_ID = "eim/node_blender"

    @contextlib.contextmanager
    def stdoutIO(self, stdout=None):
        old = sys.stdout
        if stdout is None:
            stdout = StringIO()
        sys.stdout = stdout
        yield stdout
        sys.stdout = old

    def extension_message_handle(self, topic, payload):
        python_code = payload["content"]
        logger.info(f'python_code: {python_code}')
        # extension_python.py
        try:
            output = exec(python_code, {"__builtins__": None}, {
                "bpy": bpy,
            })
        except Exception as e:
            output = e
        payload["content"] = str(output)
        message = {"payload": payload}
        self.publish(message)

    def exit_message_handle(self, topic, payload):
        self.terminate()

    @threaded
    def run(self):
        while self._running:
            time.sleep(0.5)


node = BlenderNode()
node.receive_loop_as_thread()
# node.run()
