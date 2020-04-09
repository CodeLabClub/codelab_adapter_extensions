import time
import importlib, sys
from codelab_adapter import settings
from codelab_adapter.core_extension import Extension
import zmq


class EimTriggerExtension(Extension):
    HELP_URL = "http://adapter.codelab.club/extension_guide/eim_trigger/"
    WEIGHT = 97
    
    def __init__(self):
        super().__init__()
        self.EXTENSION_ID = "eim"

    def run(self):
        module_name = "eim_trigger"
        try:
            importlib.import_module(module_name)
        except Exception as e:
            self.pub_notification(f'{e}', type="ERROR")
            return
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
