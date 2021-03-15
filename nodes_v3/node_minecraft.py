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


class MyMinecraftClient:
    def __init__(self, node=None):
        self.node = node
        self.is_connected = False
        self.mc = None
        self.mcTurtle = None

    def connect(self, ip="raspberrypi.local"):
        # 连通性？ping
        self.mc = minecraft.Minecraft.create(
            address=ip)  # 使用 Scratch 设置
        pos = self.mc.player.getTilePos()
        #Using the Minecraft Turtle
        self.mcTurtle = MinecraftTurtle(self.mc, pos)
        if self.mc:
            if self.node:
                node.pub_notification("Minecraft 已连接",
                                      type="SUCCESS")  # 由一个积木建立连接到时触发
            self.is_connected = True
            return True


class McpiNode(AdapterNode):
    NODE_ID = "eim/node_minecraft"
    REQUIREMENTS = ["mcpi", "minecraftstuff"]
    HELP_URL = "https://adapter.codelab.club/extension_guide/minecraft/"
    DESCRIPTION = "《Minecraft》是一款开放世界游戏"

    def __init__(self, **kwargs):
        super().__init__(logger=logger, **kwargs)
        self.NODE_ID = self.generate_node_id(__file__)
        self.mc_client = MyMinecraftClient(self)

    def _import_requirement_or_import(self):
        requirement = self.REQUIREMENTS
        try:
            from mcpi import minecraft
            from minecraftstuff import MinecraftTurtle
        except ModuleNotFoundError:
            self.pub_notification(f'正在安装 {" ".join(requirement)}...')
            install_requirement(requirement)
            self.pub_notification(f'{" ".join(requirement)} 安装完成')

        from mcpi import minecraft
        from minecraftstuff import MinecraftTurtle

        global minecraft, MinecraftTurtle

    def run_python_code(self, code):
        try:
            output = eval(code, {"__builtins__": None}, {
                "connect": self.mc_client.connect,
                "mc": self.mc_client.mc,
                "mcTurtle": self.mc_client.mcTurtle,
            })
        except Exception as e:
            output = e
        return output

    def extension_message_handle(self, topic, payload):
        self.logger.info(f'code: {payload["content"]}')
        message_id = payload.get("message_id")
        python_code = payload["content"]

        if (not self.mc_client.is_connected) and ("connect" not in python_code):
            self.pub_notification("未发现 Minecraft", type="WARNING")
            return

        output = self.run_python_code(python_code)
        payload["content"] = str(output)
        message = {"payload": payload}
        self.publish(message)

    def run(self):
        "避免插件结束退出"
        self._import_requirement_or_import()
        # global minecraft, MinecraftTurtle
        while self._running:
            time.sleep(0.5)


def main(**kwargs):
    try:
        node = McpiNode(**kwargs)
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        # node.logger.debug("KeyboardInterrupt") # work mac
        if node._running:
            node.terminate()  # Clean up before exiting.


if __name__ == "__main__":
    main()