import time
import subprocess

from scratch3_adapter import settings
from scratch3_adapter.core_extension import Extension

class HassExtension(Extension):
    def __init__(self):
        name = type(self).__name__ # class name
        super().__init__(name)

    def run(self):
        # run 会被作为线程调用,勾选之后调用: 启动hass进程
        hass = subprocess.Popen("hass", shell = True)
        while self._running:
            # 把while当成阻塞机制
            time.sleep(1)
        #取消勾选: 关闭进程
        subprocess.Popen.kill(hass)

export = HassExtension
