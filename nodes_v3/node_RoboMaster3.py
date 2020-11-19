'''
pip install robomaster codelab_adapter_client --upgrade
doc: https://robomaster-dev.readthedocs.io/zh_CN/latest/python_sdk/beginner_ep.html
仅支持
    macOS >= 10.15
    Window amd64

策略作为外部 Node，能够和Adapter通信

使用 EIM 测试: eim/extension_RoboMasterEP3
''' 

import time
from loguru import logger
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import get_or_create_node_logger_dir
from robomaster import robot
from robomaster import blaster

node_logger_dir = get_or_create_node_logger_dir()
debug_log = str(node_logger_dir / "debug.log")
logger.add(debug_log, rotation="1 MB", level="DEBUG")


class EP3Node(AdapterNode):
    NODE_ID = "eim/extension_RoboMasterEP3"
    HELP_URL = "https://adapter.codelab.club/extension_guide/RoboMaster_EP2/"
    DESCRIPTION = "RoboMaster EP 3.0"

    def __init__(self):
        super().__init__(logger=logger)
        self.ep_robot = None

    def init_device(self, timeout=5, conn_type="sta"):
        '''
        conn_type
            sta 机器人接入局域网
            ap 机器人作为热点
        '''
        # todo timeout
        self.ep_robot = robot.Robot()
        self.ep_robot.initialize(conn_type=conn_type)
        self.pub_notification("Device(RoboMaster) Connected!", type="SUCCESS")

    def run_python_code(self, code):
        try:
            # 允许用户传入连接参数 init_device
            output = eval(code, {"__builtins__": None}, {"ep_robot": self.ep_robot, "blaster": blaster, "init_device": self.init_device})
        except Exception as e:
            output = e
        return output

    def extension_message_handle(self, topic, payload):
        self.logger.info(f'code: {payload["content"]}')
        message_id = payload.get("message_id")
        python_code = payload["content"]
        if self.ep_robot:
            output = self.run_python_code(python_code)
            payload["content"] = str(output)
            message = {"payload": payload}
            self.publish(message)

    def run(self):
        "避免插件结束退出"
        try:
            self.init_device()
        except Exception as e:
            self.logger.error(e)
            self.pub_notification(str(e), type="ERROR")
            return
        while self._running:
            time.sleep(0.5)

    def terminate(self, **kwargs):
        try:
            if self.ep_robot:
                self.ep_robot.close()
                self.ep_robot = None
        except Exception as e:
            self.pub_notification(str(e), type="ERROR")
            time.sleep(0.1)
        super().terminate(**kwargs)

if __name__ == "__main__":
    try:
        node = EP3Node()
        node.receive_loop_as_thread()
        node.run()
    except:
        if node._running:
            node.terminate()