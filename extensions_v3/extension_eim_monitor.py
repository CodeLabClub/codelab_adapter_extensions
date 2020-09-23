import importlib
import queue
import sys
import time

from codelab_adapter import settings
from codelab_adapter.core_extension import Extension


class EimMonitorExtension(Extension):
    
    NODE_ID = "eim"
    HELP_URL = "http://adapter.codelab.club/extension_guide/eim_monitor/"
    WEIGHT = 96
    DESCRIPTION = "响应一条eim消息"
    
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        

        self.q = queue.Queue()

    def extension_message_handle(self, topic, payload):
        content = payload["content"]
        response = sys.modules["eim_monitor"].monitor(content, self.logger)
        payload["content"] = response
        message = {"payload": payload}
        self.publish(message)

    def run(self):
        module_name = "eim_monitor"
        # todo try else
        try:
            importlib.import_module(module_name)
        except Exception as e:
            self.pub_notification(f'{e}', type="ERROR")
        else:
            module = sys.modules["eim_monitor"]
            importlib.reload(module)

            while self._running:
                time.sleep(0.1)


export = EimMonitorExtension
