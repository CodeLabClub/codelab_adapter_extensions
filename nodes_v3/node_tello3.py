# pip install https://github.com/wwj718/DJITelloPy/archive/master.zip
import time
import json
import socket
from loguru import logger
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.thing import AdapterThing
from codelab_adapter_client.utils import get_or_create_node_logger_dir

from djitellopy import Tello

node_logger_dir = get_or_create_node_logger_dir()
debug_log = str(node_logger_dir / "debug.log")
logger.add(debug_log, rotation="1 MB", level="DEBUG")


class TelloProxy(AdapterThing):
    '''
    对象内部可能出现意外错误，重置积木（重启整个插件）
    self.thing = Tello() 由于是udp 所以与wifi的通断 不影响， self.thing总是可用
    '''
    def __init__(self, node_instance):
        super().__init__(thing_name="Tello",
                         node_instance=node_instance)

    def list(self, timeout=5) -> list:
        if not self.thing:
            self.thing = Tello()
        self.thing.RESPONSE_TIMEOUT = timeout
        logger.debug(f"self.thing: {self.thing}")
        try:
            # if True:  # self.thing.connect():  # RESPONSE_TIMEOUT 7 ，判断是否可连接
            # logger.debug(f"self.thing.connect(): {self.thing.connect()}")
            self.thing.connect()  # 返回True有问题，如果没有飞机，就会except
            return ["192.168.10.1"]
        except Exception as e:  # timeout
        # except:
            # self.thing.connect() except
            logger.debug(f'error: {str(e)}')
            self.node_instance.pub_notification(str(e),
                                                type="ERROR")
            return []

    def connect(self, ip, timeout=5):
        # 修改 self.thing
        if not self.thing:
            self.thing = Tello()
        is_connected = self.thing.connect()  # 幂等操作 ，udp
        self.is_connected = is_connected
        return True

    def status(self, **kwargs) -> bool:
        # check status
        # query thing status, 与设备通信，检查 is_connected 状态，修改它
        return self.thing.connect()  # 超时7秒

    def disconnect(self):
        self.is_connected = False
        try:
            if self.thing:
                self.thing.clientSocket.close()  # 断开，允许本地其他client（如python client）
        except Exception:
            pass
        self.thing = None


class Tello3Node(AdapterNode):
    NODE_ID = "eim/node_tello3"
    HELP_URL = "https://adapter.codelab.club/extension_guide/tello3/"
    DESCRIPTION = "tello 3.0"  # list connect
    VERSION = "3.0.0"

    def __init__(self):
        super().__init__(logger=logger)
        self.tello = TelloProxy(self)

    def run_python_code(self, code):
        try:
            output = eval(
                code,
                {"__builtins__": None},
                {
                    "tello": self.tello.thing,  # 直接调用方法
                    "connect": self.tello.connect,
                    "disconnect": self.tello.disconnect,
                    "list": self.tello.list,
                })
        except Exception as e:
            output = e
        return output

    def extension_message_handle(self, topic, payload):
        self.logger.info(f'code: {payload["content"]}')
        python_code = payload["content"]
        output = self.run_python_code(python_code)
        try:
            output = json.dumps(output)
        except Exception:
            output = str(output)
        payload["content"] = output
        message = {"payload": payload}
        self.publish(message)

    # self.pub_notification(str(e), type="ERROR")

    def run(self):
        while self._running:
            time.sleep(0.5)

    def terminate(self, **kwargs):
        try:
            self.tello.disconnect()
        except Exception:
            pass
        super().terminate(**kwargs)


if __name__ == "__main__":
    try:
        node = Tello3Node()
        node.receive_loop_as_thread()
        node.run()
    except Exception as e:
        if node._running:
            node.pub_notification(str(e), type="ERROR")
            time.sleep(0.1)
            node.terminate()
