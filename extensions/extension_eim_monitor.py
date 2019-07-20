import time
import importlib, sys
from codelab_adapter import settings
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import  ui_error

class EimMonitorExtension(Extension):
    def __init__(self):
        '''
        参考 home assistant
        '''
        name = type(self).__name__  # class name
        super().__init__(name)

    def run(self):
        try:
            from eim_monitor import monitor
        except Exception as e:
            ui_error('eim_script error',str(e))
            return 
        module = sys.modules["eim_monitor"]
        importlib.reload(module)
        while self._running:
            # monitor返回值被pub
            # rate = 10
            # time.sleep(1/rate) # 默认频率是每秒运行十次这个函数
            try:
                response = monitor()
                if response:
                    message = {"topic": "eim", "payload": response}
                    self.publish(message)
            except:
                ui_error('eim_script error',str(e))

export = EimMonitorExtension
