import time
import subprocess
import platform

from scratch3_adapter import settings
from scratch3_adapter.core_extension import Extension

'''
预先按照好hass，全局的
'''
if (platform.system() == "Darwin"):
    cmd = "/usr/local/bin/hass" # mac
if platform.system() == "Windows":
    cmd = ""

class HassExtension(Extension):
    def __init__(self):
        name = type(self).__name__ # class name
        super().__init__(name)

    def run(self):
        # run 会被作为线程调用,勾选之后调用: 启动hass进程
        # 用户需要知道系统命令所在的绝对路径
        
        hass = subprocess.Popen(cmd , shell = True)
        while self._running:
            # 把while当成阻塞机制
            time.sleep(1)
        #取消勾选: 关闭进程
        subprocess.Popen.kill(hass)

export = HassExtension
