import time
import importlib, sys
from codelab_adapter import settings
from codelab_adapter.core_extension import Extension
import zmq


class EimTriggerExtension(Extension):
    NODE_ID = "eim"
    HELP_URL = "http://adapter.codelab.club/extension_guide/eim_trigger/"
    WEIGHT = 97
    DESCRIPTION = "触发一条eim消息"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self):
        module_name = "eim_trigger"
        try:
            importlib.import_module(module_name)
        except Exception as e:
            self.pub_notification(f'{e}', type="ERROR")
        else:
            module = sys.modules[module_name]
            importlib.reload(module)
            while self._running:
                try:
                    response = sys.modules[
                        module_name].trigger()
                    if response:
                        message = {"payload": {"content": response}}
                        self.publish(message)
                except zmq.error.ZMQError as e:
                    self.logger.error(f'{e}')
                except Exception as e:
                    self.logger.error(f'{e}')
                    self.pub_notification(f'{e}')


export = EimTriggerExtension
