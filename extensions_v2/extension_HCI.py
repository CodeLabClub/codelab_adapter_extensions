'''
HCI: human–machine interaction
本插件支持将任何输入映射为鼠标键盘行为

requirement:
    pip3 install pyautogui --user

PyAutoGUI only runs on Windows, Mac, and Linux.
If you lose control and need to stop the current PyAutoGUI function, keep moving the mouse cursor up and to the left. 

tips:
    currentMouseX, currentMouseY = pyautogui.position()
    pyautogui.moveTo(100, 150)
    pyautogui.click()
    pyautogui.moveRel(None, 10)  # move mouse 10 pixels down
    pyautogui.typewrite('Hello world!', interval=0.25)

todo:
    在Scratch3.0中写一个能自己写程序的程序
'''

from codelab_adapter.core_extension import ControllerExtension
from codelab_adapter.utils import get_server_file_path


class HCIControllerExtension(ControllerExtension):
    '''
    use to control VectorNode(server)
    '''

    def __init__(self):
        super().__init__()
        self.server_extension_id = "eim/HCI"
        self.EXTENSION_ID = f"{self.server_extension_id}/control"  # default eim
        self.server_file = get_server_file_path("HCI_server.py")


export = HCIControllerExtension
