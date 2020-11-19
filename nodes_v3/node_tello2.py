# pip install https://github.com/wwj718/DJITelloPy/archive/master.zip
import time
from loguru import logger
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import get_or_create_node_logger_dir
from djitellopy import Tello

node_logger_dir = get_or_create_node_logger_dir()
debug_log = str(node_logger_dir / "debug.log")
logger.add(debug_log, rotation="1 MB", level="DEBUG")


class Tello2Node(AdapterNode):
    NODE_ID = "eim/node_tello2"
    HELP_URL = "https://adapter.codelab.club/extension_guide/tello2/"
    DESCRIPTION = "tello 2.0"

    def __init__(self):
        super().__init__(logger=logger)

    def run_python_code(self, code):
        try:
            output = eval(code, {"__builtins__": None}, {"tello": self.tello})
        except Exception as e:
            output = e
        return output

    def extension_message_handle(self, topic, payload):
        self.logger.info(f'code: {payload["content"]}')
        message_id = payload.get("message_id")
        python_code = payload["content"]
        output = self.run_python_code(python_code)
        payload["content"] = str(output)
        message = {"payload": payload}
        self.publish(message)

    def run(self):
        "避免插件结束退出"
        try:
            self.tello = Tello()
        except Exception as e:
            self.logger.error(e)
            self.pub_notification(str(e), type="ERROR")
            return
        while self._running:
            time.sleep(0.5)

    def terminate(self, **kwargs):
        try:
            self.tello.__del__()
        except:
            pass
        super().terminate(**kwargs)

if __name__ == "__main__":
    try:
        node = Tello2Node()
        node.receive_loop_as_thread()
        node.run()
    except Exception as e:
        # node.logger.debug("KeyboardInterrupt") # work mac
        if node._running:
            node.pub_notification(str(e), type="ERROR")
            time.sleep(0.1)
            node.terminate()  # Clean up before exiting.