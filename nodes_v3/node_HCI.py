'''
pip3 install gpiozero pigpio --user
# docs: https://gpiozero.readthedocs.io/en/stable/remote_gpio.html
'''
# GPIOZERO_PIN_FACTORY=pigpio PIGPIO_ADDR= "raspberrypi.local"# 192.168.1.3

import queue
import time
import pyautogui # try ，如果没有安装 抛出消息
from codelab_adapter_client import AdapterNode


class HCINode(AdapterNode):
    '''
    Everything Is Message
    ref: https://github.com/CodeLabClub/codelab_adapter_extensions/blob/master/extensions_v2/extension_python_kernel.py
    '''

    def __init__(self):
        super().__init__()
        self.NODE_ID = self.generate_node_id(__file__)  # default: eim
        self.q = queue.Queue()

    def extension_message_handle(self, topic, payload):
        # self.q.put(payload)
        # payload = self.q.get()
        message_id = payload.get("message_id")
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

    def exit_message_handle(self, topic, payload):
        self.terminate()

    def run(self):
        while self._running:
            time.sleep(0.5)


if __name__ == "__main__":
    try:
        node = HCINode()
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        node.terminate()  # Clean up before exiting.s
    except Exception as e:
        node.logger.error(str(e))
        node.pub_notification(str(e), type="ERROR")
        time.sleep(0.05)
        node.terminate()  # Clean up before exiting.