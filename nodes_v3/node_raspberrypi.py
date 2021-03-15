'''
pip install gpiozero pigpio --user
# docs: https://gpiozero.readthedocs.io/en/stable/remote_gpio.html
'''
import contextlib
import os  # env
import sys
import time
from io import StringIO
from time import sleep

from loguru import logger

from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import get_or_create_node_logger_dir, install_requirement

# GPIOZERO_PIN_FACTORY=pigpio PIGPIO_ADDR= "raspberrypi.local"# 192.168.1.3
# os.environ["GPIOZERO_PIN_FACTORY"] = "pigpio"
# os.environ["PIGPIO_ADDR"] = "raspberrypi.local"

node_logger_dir = get_or_create_node_logger_dir()
debug_log = str(node_logger_dir / "debug.log")
logger.add(debug_log, rotation="1 MB", level="DEBUG")


class RaspberryPi:
    def __init__(self, node=None):
        self.node = node
        self.is_connected = False
        self.factory = None
        self.led = None

    def connect(self, ip="raspberrypi.local"):
        self.factory = PiGPIOFactory(host=ip)  # 192.168.1.3
        if self.factory:
            if self.node:
                node.pub_notification(
                    "RaspberryPi 已连接",
                    type="SUCCESS")  # 由一个积木建立连接到时触发
            self.is_connected = True
            self.led = LED(17, pin_factory=self.factory)
            return True


class RPINode(AdapterNode):
    NODE_ID = "eim/node_raspberrypi"
    HELP_URL = "https://adapter.codelab.club/extension_guide/rpi_gpio/"
    DESCRIPTION = "使用 gpiozero 对树莓派进行编程"
    REQUIREMENTS = ["gpiozero", "pigpio"]

    def __init__(self, **kwargs):
        super().__init__(logger=logger, **kwargs)
        self.rpi = RaspberryPi(self)

    def _install_requirement_or_import(self):
        requirement = self.REQUIREMENTS
        try:
            import gpiozero, pigpio
        except ModuleNotFoundError:
            self.pub_notification(f'正在安装 {" ".join(requirement)}...')
            install_requirement(requirement)
            self.pub_notification(f'{" ".join(requirement)} 安装完成')
        from gpiozero import LED
        from gpiozero.pins.pigpio import PiGPIOFactory
        global LED, PiGPIOFactory

    def run_python_code(self, code):
        try:
            output = eval(code, {"__builtins__": None}, {
                "connect": self.rpi.connect,
                "led": self.rpi.led,
                "factory": self.rpi.factory
            })
        except Exception as e:
            output = e
        return output

    def extension_message_handle(self, topic, payload):
        self.logger.info(f'code: {payload["content"]}')
        python_code = payload["content"]
        if (not self.rpi.is_connected) and ("connect" not in python_code):
            self.pub_notification("未发现 RaspberryPi", type="WARNING")
            return
        output = self.run_python_code(python_code)
        payload["content"] = str(output)
        message = {"payload": payload}
        self.publish(message)

    def run(self):
        "避免插件结束退出"
        self._install_requirement_or_import()
        while self._running:
            time.sleep(0.5)


def main(**kwargs):
    try:
        node = RPINode(**kwargs)
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        # node.logger.debug("KeyboardInterrupt") # work mac
        if node._running:
            node.terminate()  # Clean up before exiting.


if __name__ == "__main__":
    main()