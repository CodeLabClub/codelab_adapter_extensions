# pip3 install codelab_adapter_client # blender
'''
运行在 blender 环境下
'''
import sys
import time

from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import threaded
import bpy  #
from loguru import logger


class BlenderNode(AdapterNode):
    NODE_ID = "eim/node_blender"

    def __init__(self):
        super().__init__()

    def run_python_code(self, code):
        try:
            output = eval(code, {"__builtins__": None}, {"bpy": bpy})
        except Exception as e:
            output = e
        return output

    def extension_message_handle(self, topic, payload):
        python_code = payload["content"]
        logger.info(f'python_code: {python_code}')
        output = self.run_python_code(python_code)

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
