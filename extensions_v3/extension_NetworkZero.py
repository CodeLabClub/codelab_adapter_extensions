import queue
import time

from codelab_adapter.core_extension import Extension
from codelab_adapter.nw0_adapter import Nw0Helper

nw0_message_queue = queue.Queue()


class NW0Extension(Extension):

    NODE_ID = "eim/extension_NetworkZero"
    HELP_URL = "http://adapter.codelab.club/extension_guide/NetworkZero/"
    VERSION = "1.0"  # extension version
    DESCRIPTION = "NetworkZero"
    WEIGHT = 94.1
    REQUIRES_ADAPTER = ">= 3.4.0"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nw0Helper = Nw0Helper(self, nw0_message_queue)

    def run_python_code(self, code):
        # fork from python extension
        try:
            output = eval(code, {"__builtins__": None}, {
                "nw0Helper": self.nw0Helper,
            })
        except Exception as e:
            output = str(e)
        return output

    def extension_message_handle(self, topic, payload):
        self.logger.info(f'python code: {payload["content"]}')
        message_id = payload.get("message_id")
        python_code = payload["content"]
        output = self.run_python_code(python_code)
        payload["content"] = output
        message = {"payload": payload}  # 无论是否有message_id都返回
        self.publish(message)

    def run(self):
        "避免插件结束退出"
        while self._running:
            time.sleep(0.05)
            if not nw0_message_queue.empty():

                (name, nw0_message) = nw0_message_queue.get()
                self.logger.debug(
                    f'(name, nw0_message)(to scrtch) -> {(name, nw0_message)}')
                message = self.message_template()
                # pub to scratch
                message["payload"]["content"] = {
                    "name": name,
                    "message": nw0_message
                }
                self.publish(message)


export = NW0Extension