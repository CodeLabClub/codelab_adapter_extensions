import time
import os
import subprocess
import platform
import pathlib
from loguru import logger
from codelab_adapter_client import AdapterNode


def get_adapter_home_path():
    return pathlib.Path.home() / "codelab_adapter"


def get_python3_path(PYTHON3_PATH=None):
    # If it is not working,  Please replace python3_path with your local python3 path. how to find our local python3 path: which python3 (*nix)
    if (platform.system() == "Darwin"):
        path = "/usr/local/bin/python3"
    if platform.system() == "Windows":
        path = "python"
    if platform.system() == "Linux":
        path = "/usr/bin/python3"
    return path


def subprocess_args(include_stdout=True):
    '''
    only Windows
    '''
    if hasattr(subprocess, 'STARTUPINFO'):
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        env = os.environ
    else:
        si = None
        env = None

    ret = {}
    ret.update({
        'stdin': subprocess.PIPE,
        'stderr': subprocess.PIPE,
        'startupinfo': si,
        'env': env
    })
    return ret


class JupyterlabNode(AdapterNode):
    '''
    The Jupyterlab Node

    /usr/local/bin/python3 -m jupyterlab --notebook-dir="~"
    '''
    def __init__(self):
        super().__init__()
        self.EXTENSION_ID = "eim/JupyterlabNode"

    def run(self):
        adapter_home_path = get_adapter_home_path()
        python_path = get_python3_path()
        cmd = f'{python_path} -m jupyterlab --notebook-dir="{adapter_home_path}"'
        
        try:
            # block...
            subprocess.check_call(cmd, shell=True, **subprocess_args())
        except:
            # to install jupyterlab
            USE_CN_PIP_MIRRORS = "-i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com" # settings
            install_jupyterlab_cmd = f'{python_path} -m pip install jupyterlab {USE_CN_PIP_MIRRORS}'
            self.pub_notification(f"jupyterlab is being installed...")
            output = subprocess.check_call(install_jupyterlab_cmd, shell=True, **subprocess_args())
            if output == 0:
                # todo: log to adapter home # adapter utils
                self.logger.info("jupyterlab installed!")
                self.pub_notification("jupyterlab installed!")
                self.pub_notification("ready to open jupyterlab...")
                subprocess.check_call(cmd, shell=True, **subprocess_args())
            else:
                self.logger.error(f"jupyterlab install error!")
                self.pub_notification(f"jupyterlab install error!")

if __name__ == "__main__":
    try:
        node = JupyterlabNode()
        node.receive_loop_as_thread() # receive_loop_as_thread should before node.run() to create message channel
        node.run()
    except KeyboardInterrupt:
        node.terminate()  # Clean up before exiting.