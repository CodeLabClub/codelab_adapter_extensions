'''
pip install gpiozero pigpio --user
# docs: https://gpiozero.readthedocs.io/en/stable/remote_gpio.html
'''
from io import StringIO
import contextlib
import sys
import time
import os  # env

from loguru import logger
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import get_or_create_node_logger_dir

# GPIOZERO_PIN_FACTORY=pigpio PIGPIO_ADDR= "raspberrypi.local"# 192.168.1.3
# os.environ["GPIOZERO_PIN_FACTORY"] = "pigpio"
# os.environ["PIGPIO_ADDR"] = "raspberrypi.local"

from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

node_logger_dir = get_or_create_node_logger_dir()
debug_log = str(node_logger_dir / "debug.log")
logger.add(debug_log, rotation="1 MB", level="DEBUG")


class RPINode(AdapterNode):
    def __init__(self):
        super().__init__(logger=logger)
        self.NODE_ID = self.generate_node_id(__file__)
        self.factory = PiGPIOFactory(host='raspberrypi.local')  # 192.168.1.3
        # 反馈 连接成功， 与失败
        self.led = LED(17, pin_factory=self.factory)

    def run_python_code(self, code):
        try:
            output = eval(code, {"__builtins__": None}, {
                "led": self.led,
                "factory": self.factory
            })
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


if __name__ == "__main__":
    try:
        node = RPINode()
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        # node.logger.debug("KeyboardInterrupt") # work mac
        if node._running:
            node.terminate()  # Clean up before exiting.