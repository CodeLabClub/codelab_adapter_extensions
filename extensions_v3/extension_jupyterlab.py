import os
import pathlib
import platform
import subprocess
import sys
import time

from codelab_adapter.core_extension import Extension
from codelab_adapter.launcher import launch_proc  # just like subprocess.Popen, but better cross-platform support
from codelab_adapter.local_env import EnvManage
from codelab_adapter.utils import get_python3_path, is_win, get_pip_cn_i_option
from codelab_adapter.settings import USE_CN_PIP_MIRRORS


def get_adapter_home_path():
    return pathlib.Path.home() / "codelab_adapter"


class JupyterlabExtension(Extension):
    HELP_URL = "http://adapter.codelab.club/extension_guide/eim_trigger/"
    WEIGHT = 97

    def __init__(self):
        super().__init__()
        self.NODE_ID = self.generate_node_id(
            __file__)  # extension_jupyterlab.py -> "eim/extension_jupyterlab"

        self.adapter_home_path = get_adapter_home_path()
        self.python_path = get_python3_path()
        self.env_manage = EnvManage(self.logger)
        self.jupyter_proc = None

    def install_jupyter(self):  # to install jupyterlab
        if USE_CN_PIP_MIRRORS:
            cn_i_option = get_pip_cn_i_option()  # pip xxx -i cn_i_option
            install_jupyterlab_cmd = f'{self.python_path} -m pip install jupyterlab -i {cn_i_option}'
            self.pub_notification(f"jupyterlab is being installed...")
            self.install_proc = launch_proc(
                install_jupyterlab_cmd,
                shell=True,
                logger=self.logger,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)  # work with windows
            res = self.install_proc.communicate()
            self.logger.debug(res)
            stdout, stderr = res
            self.logger.info("jupyterlab installed!")
            self.pub_notification("jupyterlab installed!")
            self.env_manage.set_env(None)  # update env
            self.pub_notification("ready to open jupyterlab...")
            if stderr:
                stderr = stderr.decode()
                self.logger.error(stderr)
                self.pub_notification(f"{stderr}")
            self.run_jupyterlab()

    def run_jupyterlab(self):
        cmd = f'{self.python_path} -m jupyterlab --notebook-dir="{self.adapter_home_path}"'
        try:
            self.jupyter_proc = launch_proc(
                cmd,
                shell=True,
                logger=self.logger,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)  # work with windows
        except Exception as e:
            self.pub_notification(str(e), type="ERROR")

    def run(self):
        env = self.env_manage.get_env()  # the local env, todo: docs
        if not env["local Python3"].get("path"):
            html_message = f'缺少 Python3，<a target="_blank" href="https://adapter.codelab.club/Python_Projects/install_python/">帮助文档</a>'
            self.pub_html_notification(html_message)
            return
            
        if not env["treasure box"].get("jupyterlab"):
            self.install_jupyter()
        else:
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
                self.jupyter_proc.kill()  # 尝试发送信号，然后关闭
                self.jupyter_proc.wait()
                # todo win: stop
                self.pub_notification("jupyterlab stopped")
                time.sleep(0.1)
            super().terminate()


export = JupyterlabExtension
