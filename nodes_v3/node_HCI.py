'''
HCI: human–machine interaction
本插件支持将任何输入映射为鼠标键盘行为

PyAutoGUI only runs on Windows, Mac, and Linux.
If you lose control and need to stop the current PyAutoGUI function, keep moving the mouse cursor up and to the left. 

tips:
    currentMouseX, currentMouseY = pyautogui.position()
    pyautogui.moveTo(100, 150)
    pyautogui.click()
    pyautogui.moveRel(None, 10)  # move mouse 10 pixels down
    pyautogui.typewrite('Hello world!', interval=0.25)

'''

import queue
import time
# import pyautogui  # todo 自动安装
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import get_or_create_node_logger_dir, install_requirement


class HCINode(AdapterNode):
    '''
    Everything Is Message
    ref: https://github.com/CodeLabClub/codelab_adapter_extensions/blob/master/extensions_v2/extension_python_kernel.py
    '''
    NODE_ID = "eim/node_HCI"
    WEIGHT = 98
    HELP_URL = "https://adapter.codelab.club/extension_guide/HCI/"
    DESCRIPTION = "接管鼠标键盘"
    VERSION = "1.1.0"
    REQUIREMENTS = ["pyautogui"]

    def __init__(self):
        super().__init__()
        self.q = queue.Queue()

    def _import_requirement_or_import(self):
        requirement = self.REQUIREMENTS
        try:
            import pyautogui
        except ModuleNotFoundError:
            self.pub_notification(f'正在安装 {" ".join(requirement)}...')
            # 只有 local python 下才可用，adapter内置的python无法使用pip（extension）
            install_requirement(requirement)
            self.pub_notification(f'{" ".join(requirement)} 安装完成')
        import pyautogui  # 使用点语法 from x import * 不在顶层 无效
        global pyautogui

    def extension_message_handle(self, topic, payload):
        # self.q.put(payload)
        # payload = self.q.get()
        message_id = payload.get("message_id")
        python_code = payload["content"]
        try:
            output = eval(python_code, {"__builtins__": None}, {
                "pyautogui": pyautogui,
            })
        except Exception as e:
            output = e
        payload["content"] = str(output)
        message = {"payload": payload}
        self.publish(message)

    def run(self):
        self._import_requirement_or_import()
        while self._running:
            time.sleep(0.5)


if __name__ == "__main__":
    try:
        node = HCINode()
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        node.terminate()  # Clean up before exiting.s
    except Exception as e:
        node.logger.error(str(e))
        node.pub_notification(str(e), type="ERROR")
        time.sleep(0.05)
        node.terminate()  # Clean up before exiting.