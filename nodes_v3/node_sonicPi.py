'''
pip install python-sonic --user
'''
import sys
import time
import os  # env
from loguru import logger
from codelab_adapter_client import AdapterNode  # codelab_adapter_client 确保已经安装，由adapter维护，首次启动时，检查version
from codelab_adapter_client.utils import get_or_create_node_logger_dir, install_requirement

# GPIOZERO_PIN_FACTORY=pigpio PIGPIO_ADDR= "raspberrypi.local"# 192.168.1.3
# os.environ["GPIOZERO_PIN_FACTORY"] = "pigpio"
# os.environ["PIGPIO_ADDR"] = "raspberrypi.local"

node_logger_dir = get_or_create_node_logger_dir()
debug_log = str(node_logger_dir / "debug.log")
logger.add(debug_log, rotation="1 MB", level="DEBUG")


class SonicPiNode(AdapterNode):
    NODE_ID = "eim/node_sonicPi"
    REQUIREMENTS = ["python-sonic"]
    HELP_URL = "https://adapter.codelab.club/extension_guide/sonicPi/"
    DESCRIPTION = "Sonic Pi 是可编程的音乐创作和演奏工具"

    def __init__(self, **kwargs):
        super().__init__(logger=logger, **kwargs)

    def _import_requirement_or_import(self):
        requirement = self.REQUIREMENTS
        try:
            import psonic
        except ModuleNotFoundError:
            self.pub_notification(f'正在安装 {" ".join(requirement)}...')
            # 只有 local python 下才可用，adapter内置的python无法使用pip（extension）
            install_requirement(requirement)
            self.pub_notification(f'{" ".join(requirement)} 安装完成')
        import psonic  # 使用点语法 from x import * 不在顶层 无效
        global psonic

    def run_python_code(self, code):
        try:
            output = eval(code, {"__builtins__": None}, {"psonic": psonic}) #  psonic 全局
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
        while self._running:
            time.sleep(0.5)


def main(**kwargs):
    try:
        node = SonicPiNode(**kwargs)
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        # node.logger.debug("KeyboardInterrupt") # work mac
        if node._running:
            node.terminate()  # Clean up before exiting.


if __name__ == "__main__":
    main()