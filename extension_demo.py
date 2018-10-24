import time

from scratch3_adapter import settings
from scratch3_adapter.core_extension import Extension

class DemoExtension(Extension):
    def __init__(self):
        '''
        继承 Extension 之后你将获得:

            self.logger  日志，日志目录在home目录下的 scratch3_adapter
            self.read 读取来自scratch的json消息
            self.publish 把json发往scratch
        高级:
            self._actuator_sub 硬件接收来自scratch的控制指令
            self._sensor_pub   硬件发布传感器的数据(发往scratch)
        '''
        name = type(self).__name__ # class name
        super().__init__(name)

    def run(self):
        # run 会被作为线程调用
        while self._running:
            message = self.read()
            self.logger.info("message:%s",str(message))

export = DemoExtension
