'''
WiFi radio
'''

import queue
import time
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import install_requirement

try:
    from microblocks_wifi_radio import Radio
except ModuleNotFoundError:
    REQUIREMENTS = ["microblocks_wifi_radio"]
    install_requirement(REQUIREMENTS)
    from microblocks_wifi_radio import Radio


class WifiRadioNode(AdapterNode):
    NODE_ID = "eim/node_wifi_radio"
    WEIGHT = 98
    HELP_URL = "https://adapter.codelab.club/extension_guide/wifi_radio/"
    DESCRIPTION = "WiFi radio"
    VERSION = "1.0.0"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.q = queue.Queue()
        self.radio = Radio()

    def extension_message_handle(self, topic, payload):
        python_code = payload["content"]
        try:
            output = eval(python_code, {"__builtins__": None}, {
                "radio": self.radio,
            })
        except Exception as e:
            output = e
        payload["content"] = str(output)
        message = {"payload": payload}
        self.publish(message)

    def run(self):
        while self._running:
            time.sleep(0.01)
            if self.radio.message_received():
                message = self.message_template()
                message["payload"]["content"] = {
                    "last_number": self.radio.last_number,
                    "last_string": self.radio.last_string,
                    "timestamp": time.time()
                }
                self.publish(message)

def main(**kwargs):
    try:
        node = WifiRadioNode(**kwargs)
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