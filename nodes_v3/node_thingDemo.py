import time
import json
import random

from codelab_adapter_client import AdapterNode
from codelab_adapter_client.thing import AdapterThing
from loguru import logger


class Robot:
    # 模拟设备
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
    '''
    该类的主要职责是实现与 Scratch UI 的兼容性
    '''
    def __init__(self, node_instance):
        super().__init__(thing_name="Robot-BB8",
                         node_instance=node_instance)

    def list(self, timeout=5) -> list:
        # 必须实现
        # scratch scan 会触发这个函数，返回值将进入 Scratch 扫描到的设备列表中。
        self.n += 1
        try:
            #  模拟有时候无法发现设备
            if self.n % 2 == 1:
                return ["192.168.10.1"]  # 随机
            else:
                self.node_instance.pub_notification(f'未发现 {self.thing_name}', type="ERROR")
                return []
        except Exception as e:
            self.node_instance.pub_notification(str(e), type="ERROR")
            return []

    def connect(self, ip, timeout=5):
        # 必须实现
        # 用户在 scratch 界面点击连接时，会触发该函数
        if not self.thing:
            self.thing = Robot()
        self.thing.connect()
        self.is_connected = True

    def status(self):
        # 必须实现
        # return self.thing.connect()
        pass

    def disconnect(self):
        # 必须实现
        # Scratch 断开设备
        self.is_connected = False
        self.thing = None


class MyNode(AdapterNode):
    NODE_ID = "eim/node_thingDemo"
    HELP_URL = "https://adapter.codelab.club/extension_guide/node_thingDemo/"
    DESCRIPTION = "thing Demo"
    VERSION = "1.0.0"

    def __init__(self, **kwargs):
        super().__init__(logger=logger, **kwargs)
        self.thing = ThingProxy(self)

    def run_python_code(self, code):
        '''
        此处定义了与外部系统（诸如Scratch）沟通的有效消息
        list: Scratch 发现设备
        connect: scratch 建立连接
        disconnect: scratch 断开连接
        thing: 可调用的对象，一般被scratch具体功能积木调用，消息是传递面向对象风格的Python代码，如 tello.takeoff()
        '''
        try:
            output = eval(
                code,
                {"__builtins__": None},
                {
                    "thing": self.thing.thing,
                    "connect": self.thing.connect,
                    "disconnect": self.thing.disconnect,
                    "list": self.thing.list,
                })
        except Exception as e:
            output = e
        return output

    def extension_message_handle(self, topic, payload):
        # 必须实现
        # 与当前插件有关的消息都流入该函数
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
        # 用于block进程，当收到进程停止消息（将切换self._running状态），则结束阻塞
        while self._running:
            time.sleep(0.5)

    def terminate(self, **kwargs):
        # 必须实现
        # 插件退出钩子，可以执行所需的资源清理（诸如释放设备）
        try:
            self.thing.disconnect()
        except Exception:
            pass
        super().terminate(**kwargs)


def main(**kwargs):
    #  入口函数，启动插件时将以独立 Python 进程运行。
    try:
        node = MyNode(**kwargs)
        node.receive_loop_as_thread()
        node.run()
    except Exception as e:
        if node._running:
            node.pub_notification(str(e), type="ERROR")
            time.sleep(0.1)
            node.terminate()


if __name__ == "__main__":
    main()