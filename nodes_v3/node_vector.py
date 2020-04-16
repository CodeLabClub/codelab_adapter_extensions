'''
# python >= 3.6
pip3 install codelab_adapter_client anki_vector --user
wget https://github.com/anki/vector-python-sdk/raw/master/examples/tutorials/01_hello_world.py
python3 01_hello_world.py  # should be ok
'''

import os
import queue
import time

from loguru import logger
import anki_vector

from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import get_or_create_node_logger_dir

# log for debug
node_logger_dir = get_or_create_node_logger_dir()
debug_log = str(node_logger_dir / "debug.log")
logger.add(debug_log, rotation="1 MB", level="DEBUG")


class VectorNode(AdapterNode):
    '''
    Everything Is Message
    ref: https://github.com/CodeLabClub/codelab_adapter_extensions/blob/master/extensions_v2/extension_python_kernel.py
    
    node pub it's status: pid
    '''
    def __init__(self):
        super().__init__(logger=logger) # todo log
        self.NODE_ID = self.generate_node_id(__file__)
        self.HELP_URL = "https://adapter.codelab.club/extension_guide/vector/"
        self.q = queue.Queue()
        # from_jupyter/extensions

    def extension_message_handle(self, topic, payload):
        self.q.put(payload)

    # exit_message_handle 只是node需要 self.ternimate()
    def exit_message_handle(self, topic, payload):
        self.terminate()

    def run(self):
        with anki_vector.Robot() as robot:
            # with 以内 vector 错误无法被捕获，sdk做了特殊处理
            self.pub_notification("Vector Connected!", type="SUCCESS")
            while self._running:
                time.sleep(0.05)
                if not self.q.empty():
                    payload = self.q.get()
                    self.logger.info(f'python: {payload}')
                    message_id = payload.get("message_id")
                    python_code = payload["content"]

                    try:
                        # 为了安全性, 做一些能力的牺牲, 放弃使用exec
                        output = eval(python_code, {"__builtins__": None}, {
                            "anki_vector": anki_vector,
                            "robot": robot
                        })
                    except Exception as e:
                        output = e
                    payload["content"] = str(output)
                    message = {"payload": payload}
                    self.publish(message)


if __name__ == "__main__":
    try:
        node = VectorNode()
        node.receive_loop_as_thread(
        )  # run extension_message_handle, noblock(threaded)
        node.run()
    except KeyboardInterrupt:
        # 依赖这个退出
        if node._running:
            node.terminate()  # Clean up before exiting.s
    except Exception as e:
        node.logger.error(str(e))  # 为何是空？
        # node.pub_notification(str(e), type="ERROR")
        if node._running:
            node.terminate()  # Clean up before exiting.
