"""
作者：Bilikyar
插件名：jupyter插件
功能：可以在Python环境里(已有jupyterlab包)通过adapter插件管理的方式管理jupyterlab服务(开关服务)
可运行平台：Windows7 以上环境; mac 和 linux 有优秀的命令行 ; 
主要用途：在没有python环境的windows电脑里，通过嵌入式python的方式，直接运行jupyterlab，详见一下链接
https://blog.just4fun.site/embeddable-python-zip-file.html
使用方法：
    1.在python主目录里面创建config.py文件,复制一下内容复制进去，通过py文件管理jupyterlab的配置.
    在我的配置文件里我关闭token、跨域限制、自动打开浏览器的功能，这样用户可以不用登录即可使用，优化用户体验,如果不
    设置配置文件的话，jupyterlab会以默认方式打开。

c.NotebookApp.allow_origin = '*'
c.NotebookApp.disable_check_xsrf = True
c.NotebookApp.open_browser = False    
c.NotebookApp.token = ''

    2.把jupyter插件下载到adapter本地插件库(adapter有下载插件的功能)，然后把adapter移到嵌入式Python
    目录里面运行即可

todo:
    支持mac和linux平台

"""

import time, threading, subprocess, os
from codelab_adapter import settings
from codelab_adapter.utils import ui_error
from codelab_adapter.core_extension import Extension


class jupyterExtension(Extension):
    def __init__(self):
        name = type(self).__name__
        super().__init__(name)
        self.currentListDir = os.listdir(".")

    def run(self):

        if "config.py" in self.currentListDir:
            cmd = ".\pythonw -m jupyterlab --config=config.py"
        else:
            cmd = ".\pythonw -m jupyterlab"


        try:
            CREATE_NO_WINDOW = 0x08000000
            jupyter_server = subprocess.Popen(cmd,creationflags=CREATE_NO_WINDOW)
            settings.running_child_procs.append(jupyter_server)
        except WindowsError: 
            if "python.exe" in self.currentListDir:
                ui_error("创建进程出错", "请安装好jupyterlab")
            else:
                ui_error("创建进程出错", "请确保adapter在python主目录下运行")
        except Exception as e: 
            ui_error("创建进程出错", e)
        else:
            self.logger.info("成功开启进程")

        while self._running:
            time.sleep(1)

        try:
            jupyter_server.terminate()
            jupyter_server.wait()
        except Exception as e: 
            ui_error("关闭进程时出错：", e)
        else:
            self.logger.info("成功关闭进程") 
        
export = jupyterExtension
