import os
import pathlib
import platform
import subprocess
import sys
import time
import signal

from codelab_adapter.core_extension import Extension
from codelab_adapter.launcher import launch_proc  # just like subprocess.Popen, but better cross-platform support
from codelab_adapter.local_env import EnvManage
from codelab_adapter.utils import get_html_message_for_no_local_python
from codelab_adapter_client.utils import get_python3_path, install_requirement, get_adapter_home_path


class JupyterlabExtension(Extension):

    NODE_ID = "eim/extension_jupyterlab"
    HELP_URL = "https://adapter.codelab.club/extension_guide/jupyterlab/"
    WEIGHT = 97
    VERSION = "1.0"  # extension version
    DESCRIPTION = "使用 JupyterLab 开始你的 Python 之旅"
    REQUIREMENTS = ["jupyterlab"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.adapter_home_path = get_adapter_home_path()
        self.python_path = get_python3_path()
        self.env_manage = EnvManage(self.logger)
        self.jupyter_proc = None

    def _install_requirement(self):  # to install jupyterlab
        self.pub_notification(f"jupyterlab is being installed...")
        output = install_requirement(self.REQUIREMENTS)
        if output == 0:
            self.pub_notification("jupyterlab installed!")
            self.env_manage.set_env(None)  # update env

    def run_jupyterlab(self):
        cmd = [
            self.python_path, "-m", "jupyterlab", "--notebook-dir",
            str(self.adapter_home_path)
        ]
        try:
            self.jupyter_proc = launch_proc(
                cmd,
                # shell=True,
                logger=self.logger,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)  # work with windows
        except Exception as e:
            self.pub_notification(str(e), type="ERROR")

    def run(self):
        env = self.env_manage.get_env()  # the local env, todo: docs
        if not env["local Python3"].get("path"):
            html_message = get_html_message_for_no_local_python()
            self.pub_html_notification(html_message)
            return

        if not env["treasure box"].get("jupyterlab"):
            self._install_requirement()
        self.pub_notification("ready to open jupyterlab...")
        self.run_jupyterlab()
        while self._running:
            time.sleep(1)

    def terminate(self):
        '''
        stop thread
        '''
        if self._running:
            self.pub_notification("try to stop jupyterlab")
            if self.jupyter_proc:
                # fuck Windows! 🖕️
                self.jupyter_proc.kill()
                # os.killpg(os.getpgid(self.jupyter_proc.pid), signal.SIGTERM)
                self.jupyter_proc.wait()
                # 启动 node 的东西 ，使用 psutil？ delegator.py？
                self.pub_notification("jupyterlab stopped")
                time.sleep(0.1)
            super().terminate()


export = JupyterlabExtension