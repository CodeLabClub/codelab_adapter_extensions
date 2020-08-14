import importlib
import sys
import time

from codelab_adapter_client import AdapterNode


class EimMonitorNode(AdapterNode):

    NODE_ID = "eim"
    HELP_URL = "http://adapter.codelab.club/extension_guide/eim_monitor/"
    WEIGHT = 97
    DESCRIPTION = "响应一条eim消息"

    def __init__(self):
        super().__init__()

    def extension_message_handle(self, topic, payload):
        content = payload["content"]
        response = sys.modules["eim_monitor"].monitor(content, self.logger)
        payload["content"] = response
        message = {"payload": payload}
        self.publish(message)

    def run(self):
        module_name = "eim_monitor"
        try:
            importlib.import_module(module_name)
        except Exception as e:
            self.pub_notification(f'{e}', type="ERROR")
            return
        module = sys.modules["eim_monitor"]
        importlib.reload(module)

        while self._running:
            time.sleep(0.1)


if __name__ == "__main__":
    try:
        node = EimMonitorNode()
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        if node._running:
            node.terminate()  # Clean up before exiting.
