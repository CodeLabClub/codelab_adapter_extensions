
'''
EIM: Everything Is Message
'''
import time
import threading
import subprocess
import serial

from codelab_adapter import settings
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import find_microbit


class HungryRobotExtension(Extension):
    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)

    def run(self):
        '''
        run 会被作为线程调用
        当前插件功能:
            往scratch不断发送信息
        '''
        port = find_microbit()
        # port = "/dev/tty.usbmodem14312"
        self.ser = serial.Serial(port, 115200, timeout=1)

        while True:
                read_message = self.read()  # json
                self.logger.info("message:", read_message)
                # zeromq
                if read_message.get("topic") == "eim":
                    data = read_message.get("payload")
                    if data == "eat":
                        # 串口写eat
                        message_bytes = b'8\n' # 8 -> eat
                        self.ser.write(message_bytes)
                # subprocess.call("say {}".format(read_message["payload"]),shell=True)

export = HungryRobotExtension
