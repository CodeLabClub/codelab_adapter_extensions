import time
import json
import random
from loguru import logger
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.thing import AdapterThing
from codelab_adapter_client.utils import get_or_create_node_logger_dir

node_logger_dir = get_or_create_node_logger_dir()
debug_log = str(node_logger_dir / "debug.log")
logger.add(debug_log, rotation="1 MB", level="DEBUG")


class Robot:
    '''
    对象内部可能出现意外错误，重置积木（client/Scratch）（重启整个插件）
    '''
    # 具体驱动
    def __init__(self):
        self.connected = False

    def connect(self):
        self.connected = True
        return "ok"

    def close(self):
        self.connected = False
        return "ok"

    def takeoff(self):
        time.sleep(1)
        return "ok"
    
    def land(self):
        time.sleep(1)
        return "ok"
    
    def move_forward(self, x):
        time.sleep(1)
        return f"forward {x}"
    
    def query_height(self):
        time.sleep(1)
        return random.randint(1, 10)


class ThingProxy(AdapterThing):
    def __init__(self, node_instance):
        # todo pydanic
        super().__init__(thing_name="Robot-BB8",
                         node_instance=node_instance)
        self.n = 0

    def list(self, timeout=5) -> list:
        # check is onlien 192.168.10.1 CONTROL_UDP_PORT = 8889
        self.n += 1
        try:
            if self.n % 2 == 1:
                return ["192.168.10.1"]  # 随机
            else:
                self.node_instance.pub_notification(f'{self.thing_name} not found', type="ERROR")
                return []
        except Exception as e:  # timeout
            self.node_instance.pub_notification(str(e), type="ERROR")
            return []

    def connect(self, ip, timeout=5):
        if not self.thing:
            # 多次连接
            self.thing = Robot()
        self.thing.connect()
        is_connected = True  # 幂等操作 ，udp
        self.is_connected = is_connected

    def status(self, **kwargs) -> bool:
        # check status
        # query thing status, 与设备通信，检查 is_connected 状态，修改它
        pass

    def disconnect(self):
        self.is_connected = False
        try:
            if self.thing:
                pass
        except Exception:
            pass
        self.thing = None


class MyNode(AdapterNode):
    NODE_ID = "eim/node_thingDemo"
    HELP_URL = "https://adapter.codelab.club/extension_guide/node_thingDemo/"
    DESCRIPTION = "thing Demo"  # list connect

    def __init__(self):
        super().__init__(logger=logger)
        self.thing = ThingProxy(self)

    def run_python_code(self, code):
        try:
            output = eval(
                code,
                {"__builtins__": None},
                {
                    "thing": self.thing.thing,  # 直接调用方法
                    "connect": self.thing.connect,
                    "disconnect": self.thing.disconnect,
                    "list": self.thing.list,
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

    def run(self):
        while self._running:
            time.sleep(0.5)

    def terminate(self, **kwargs):
        try:
            self.thing.disconnect()
        except Exception:
            pass
        super().terminate(**kwargs)


if __name__ == "__main__":
    try:
        node = MyNode()
        node.receive_loop_as_thread()
        node.run()
    except Exception as e:
        if node._running:
            node.pub_notification(str(e), type="ERROR")
            time.sleep(0.1)
            node.terminate()
