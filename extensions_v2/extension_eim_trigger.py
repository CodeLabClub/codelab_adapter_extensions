import time
import importlib, sys
from codelab_adapter import settings
from codelab_adapter.core_extension import Extension
import zmq
'''
检测文件是否存在 不存在就创建 都在插件里做
'''


class EimTriggerExtension(Extension):
    def __init__(self):
        super().__init__()
        self.EXTENSION_ID = "eim"

    def run(self):
        module_name = "eim_trigger"
        try:
            importlib.import_module(module_name)
        except Exception as e:
            self.pub_notification(f'{e}')
            return
        module = sys.modules[module_name]
        importlib.reload(module)
        while self._running:
            # monitor返回值被pub
            # rate = 10
            # time.sleep(1/rate) # 默认频率是每秒运行十次这个函数
            try:
                response = sys.modules[
                    module_name].trigger()  # 休眠1s，阻塞，stop会报错， 等待退出，todo 非守护进程
                if response:
                    message = {"payload": {"content": response}}
                    self.publish(message)
            except zmq.error.ZMQError as e:
                self.logger.error(f'{e}') # 终止之后 发不出消息
            except Exception as e:
                self.logger.error(f'{e}')
                # self.pub_notification(f'{e}')


export = EimTriggerExtension
