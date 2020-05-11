'''
pip install mcpi minecraftstuff --user
'''
from io import StringIO
import contextlib
import sys
import time
import os  # env

from loguru import logger
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import get_or_create_node_logger_dir, install_requirement

# GPIOZERO_PIN_FACTORY=pigpio PIGPIO_ADDR= "raspberrypi.local"# 192.168.1.3
# os.environ["GPIOZERO_PIN_FACTORY"] = "pigpio"
# os.environ["PIGPIO_ADDR"] = "raspberrypi.local"

node_logger_dir = get_or_create_node_logger_dir()
debug_log = str(node_logger_dir / "debug.log")
logger.add(debug_log, rotation="1 MB", level="DEBUG")


class McpiNode(AdapterNode):
    NODE_ID = "eim/node_minecraft"
    REQUIREMENTS = ["mcpi", "minecraftstuff"]

    def __init__(self):
        super().__init__(logger=logger)
        self.NODE_ID = self.generate_node_id(__file__)

    def _import_requirement_or_import(self):
        requirement = self.REQUIREMENTS
        try:
            from mcpi import minecraft
            from minecraftstuff import MinecraftTurtle
        except ModuleNotFoundError:
            self.pub_notification(f'try to install {" ".join(requirement)}...')
            install_requirement(requirement)
            self.pub_notification(f'{" ".join(requirement)} installed!')

        from mcpi import minecraft
        from minecraftstuff import MinecraftTurtle

        global minecraft, MinecraftTurtle

    def run_python_code(self, code):
        try:
            output = eval(code, {"__builtins__": None}, {
                "mc": self.mc,
                "mcTurtle": self.mcTurtle,
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
        self._import_requirement_or_import()
        # global minecraft, MinecraftTurtle
        self.mc = minecraft.Minecraft.create(address="raspberrypi.local")
        pos = self.mc.player.getTilePos()
        #Using the Minecraft Turtle
        self.mcTurtle = MinecraftTurtle(self.mc, pos)
        while self._running:
            time.sleep(0.5)


if __name__ == "__main__":
    try:
        node = McpiNode()
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        # node.logger.debug("KeyboardInterrupt") # work mac
        if node._running:
            node.terminate()  # Clean up before exiting.