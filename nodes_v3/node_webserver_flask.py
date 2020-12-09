'''
flask 学习 web 的理想工具，目标：入门

ref: https://flask.palletsprojects.com/en/1.1.x/quickstart/#a-minimal-application

0.10 之前才是 python hello.py 2013年， 之后都是 flask run
'''
import time
import os
import sys
from loguru import logger
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import get_or_create_node_logger_dir, install_requirement

# log for debug
node_logger_dir = get_or_create_node_logger_dir()
debug_log = str(node_logger_dir / "debug.log")
logger.add(debug_log, rotation="1 MB", level="DEBUG")

# 手动安装
REQUIREMENTS = ["flask"]


def _import_requirement_or_import():
    requirement = REQUIREMENTS
    try:
        from flask import Flask
    except ModuleNotFoundError:
        install_requirement(requirement)

    from flask import Flask
    global Flask

_import_requirement_or_import()

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


class WebNode(AdapterNode):
    NODE_ID = "eim/node_webserver_flask"

    def __init__(self):
        super().__init__(logger=logger)        

    def run(self, port=18081):
        app.run(host="0.0.0.0", port=18081)
    
    def terminate(self):
        logger.info("terminate!")
        # 停止当前进程 pid
        os._exit(0) # 为何无法退出？？ https://stackoverflow.com/questions/905189/why-does-sys-exit-not-exit-when-called-inside-a-thread-in-python


if __name__ == "__main__":
    try:
        node = WebNode()
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        # node.logger.debug("KeyboardInterrupt") # work mac
        if node._running:
            node.terminate()  # Clean up before exiting.
    finally:
        node.terminate()