'''
HCI: human–machine interaction
本插件支持将任何输入映射为鼠标键盘行为
'''

import queue
import time
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import install_requirement

try:
    import pyautogui
except ModuleNotFoundError:
    REQUIREMENTS = ["pyautogui"]
    install_requirement(REQUIREMENTS)
    import pyautogui


class HCINode(AdapterNode):
    NODE_ID = "eim/node_HCI"
    WEIGHT = 98
    HELP_URL = "https://adapter.codelab.club/extension_guide/HCI/"
    DESCRIPTION = "接管鼠标键盘"
    VERSION = "1.1.0"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.q = queue.Queue()

    def extension_message_handle(self, topic, payload):
        python_code = payload["content"]
        try:
            output = eval(python_code, {"__builtins__": None}, {
                "pyautogui": pyautogui,
            })
        except Exception as e:
            output = e
        payload["content"] = str(output)
        message = {"payload": payload}
        self.publish(message)

    def run(self):
        while self._running:
            time.sleep(0.5)


def main(**kwargs):
    try:
        node = HCINode(**kwargs)
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        node.terminate()  # Clean up before exiting.s
    except Exception as e:
        node.logger.error(str(e))
        node.pub_notification(str(e), type="ERROR")
        time.sleep(0.05)
        node.terminate()  # Clean up before exiting.


if __name__ == "__main__":
    main()