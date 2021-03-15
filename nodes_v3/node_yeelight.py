# python3 -m pip  install yeelight

import time

from loguru import logger
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import install_requirement

try:
    from yeelight import discover_bulbs, Bulb
except ModuleNotFoundError:
    # install_requirement(requirement)
    from yeelight import discover_bulbs, Bulb


class LightProxy:
    '''
    自维护
    支持连接多盏灯
    '''
    def __init__(self, node=None):
        self.node = node
        self.is_connected = False  # todo 装饰器， 确认某件事才往下，否则返回错误信息， require connect，每次确保某件事发生
        self.lights = []

    def _ensure_connect(self):
        if not self.is_connected:
            raise Exception("Device not connected!")

    def list(self):
        results = discover_bulbs()
        print(results)
        return [f"{i['ip']} : {i['capabilities']['model']}" for i in results]

    def connect(self, ip):
        # 允许多次连接
        '''
        if self.is_connected:
            return "Device already connected"
        '''
        for bulb in self.lights:
            if ip in str(bulb):
                break
        else:
            self.lights.append(Bulb(ip))
            
        return f"lights[{len(self.lights)-1}]"



class Yeelight2Node(AdapterNode):
    NODE_ID = "eim/node_yeelight"
    HELP_URL = "https://adapter.codelab.club/extension_guide/yeelight/"
    DESCRIPTION = "yeelight"

    def __init__(self, **kwargs):
        super().__init__(logger=logger, **kwargs)
        self.manager = LightProxy(self)  # create robot proxy object

    def run_python_code(self, code):
        try:
            output = eval(code, {"__builtins__": None}, {"manager": self.manager, "lights": self.manager.lights, "dir": dir} )
        except Exception as e:
            output = e
        return output

    def extension_message_handle(self, topic, payload):
        self.logger.info(f'code: {payload["content"]}')
        message_id = payload.get("message_id")
        python_code = payload["content"]
        output = self.run_python_code(python_code)
        payload["content"] = str(output)
        message = {"payload": payload}
        self.publish(message)

    def run(self):
        "避免插件结束退出"
        while self._running:
            time.sleep(0.5)


def main(**kwargs):
    try:
        node = Yeelight2Node(**kwargs)
        node.receive_loop_as_thread()
        node.run()
    except Exception as e:
        # node.logger.debug("KeyboardInterrupt") # work mac
        if node._running:
            node.pub_notification(str(e), type="ERROR")
            time.sleep(0.1)
            node.terminate()  # Clean up before exiting.


if __name__ == "__main__":
    main()