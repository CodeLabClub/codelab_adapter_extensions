import json
import time

from codelab_adapter_client import AdapterNode
from codelab_adapter_client.thing import AdapterThing
from codelab_adapter.led_bag import LedBag
from loguru import logger


class LedBagProxy(AdapterThing):
    '''
    该类的主要职责是实现与 Scratch UI 的兼容性
    '''
    def __init__(self, node_instance):
        super().__init__(thing_name="LedBag", node_instance=node_instance)

    def list(self, timeout=5) -> list:
        import bluetooth
        result = bluetooth.discover_devices(lookup_names=True)
        return []

    def connect(self, address, timeout=5):
        # 必须实现
        # 用户在 scratch 界面点击连接时，会触发该函数
        if not self.thing:
            self.thing = LedBag()
        is_connected = self.thing.connect(address)  # 幂等操作 ，udp
        self.is_connected = is_connected
        return True

    def status(self):
        # 必须实现
        # return self.thing.connect()
        pass

    def disconnect(self):
        # 必须实现
        # Scratch 断开设备
        self.is_connected = False
        try:
            if self.thing:
                self.thing.close()
        except Exception:
            pass
        self.thing = None


class LedBagNode(AdapterNode):
    NODE_ID = "eim/node_ledbag"
    HELP_URL = "https://adapter.codelab.club/extension_guide/ledbag/"
    DESCRIPTION = "LedBag"  # list connect
    VERSION = "1.0.0"

    def __init__(self, **kwargs):
        super().__init__(logger=logger, **kwargs)
        self.bag = LedBagProxy(self)

    def run_python_code(self, code):
        '''
        此处定义了与外部系统（诸如Scratch）沟通的有效消息
        list: Scratch 发现设备
        connect: scratch 建立连接
        disconnect: scratch 断开连接
        '''
        try:
            output = eval(
                code,
                {"__builtins__": None},
                {
                    "bag": self.bag.thing,
                    "connect": self.bag.connect,
                    "disconnect": self.bag.disconnect,
                    "list": self.bag.list,
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
            self.bag.disconnect()
        except Exception:
            pass
        super().terminate(**kwargs)


def main(**kwargs):
    #  入口函数，启动插件时将以独立 Python 进程运行。
    try:
        node = LedBagNode(**kwargs)
        node.receive_loop_as_thread()
        node.run()
    except Exception as e:
        if node._running:
            node.pub_notification(str(e), type="ERROR")
            time.sleep(0.1)
            node.terminate()


if __name__ == "__main__":
    main()