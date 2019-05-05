import time, threading, subprocess, os
from codelab_adapter import settings
from codelab_adapter.core_extension import Extension


class jupyterExtension(Extension):
    def __init__(self):
        name = type(self).__name__
        super().__init__(name)

    def run(self):
        try:
            os.chdir("python")
        except Exception as e: 
            self.logger.info("已在Python目录:%s",e)

        cmd = "python -m IPython notebook --config=config.py"

        try:
            jupyter_server = subprocess.Popen(cmd,shell=False)
            settings.running_child_procs.append(jupyter_server)
        except Exception as e: 
            self.logger.info("创建进程出错:%s",e)
        else:
            self.logger.info("成功开启进程")

        while self._running:
            time.sleep(1)

        try:
            jupyter_server.terminate()
            jupyter_server.wait()
        except Exception as e: 
            self.logger.info("无法关闭进程:%s",e)
        else:
            self.logger.info("成功关闭进程") 
        
export = jupyterExtension