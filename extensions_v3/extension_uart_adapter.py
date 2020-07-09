# list ports serial.tools.list_ports
# set port
# write xxx
# read
'''
import serial
from serial.tools.list_ports import comports as list_serial_ports

for i in list_serial_ports():print(i[0])

python -m serial.tools.miniterm <port_name> -h
python -m serial.tools.list_ports

>>> import serial
>>> ser = serial.Serial('/dev/ttyUSB0')  # open serial port
>>> print(ser.name)         # check which port was really used
>>> ser.write(b'hello')     # write a string
>>> ser.close()             # close port

with serial.Serial() as ser:
    ser.baudrate = 19200
    ser.port = 'COM1'
    ser.open()
    ser.write(b'hello')

help 与 microbit 一起做实验。读输入
    makecode 写测试

交互式

usage
    serialHelper.write("a")

刷新端口

todo
    parity 启用奇偶校验
'''

import time
import serial
from serial.tools.list_ports import comports as list_serial_ports
from codelab_adapter.core_extension import Extension


class serialHelper:
    # 每当连接新的port 就把既有的断掉
    def __init__(self, extensionInstance):
        self.extensionInstance = extensionInstance
        self.logger = extensionInstance.logger
        self.port = None  # 当前连接的port
        self.ser = None

    def connect(self, port, **kwargs):
        self.logger.debug(f"args: {kwargs}")
        if self.ser:
            self.ser.close()
        # 默认支持microbit, timeout 默认不超过scratch的积木 5s (4.5)
        if not kwargs.get("baudrate", None):
            kwargs["baudrate"] = 115200
        if not kwargs.get("timeout", None):
            kwargs["timeout"] = 4.5

        self.ser = serial.Serial(port, **kwargs)
        if self.ser.name:
            return "ok"

    def list_ports(self):
        return [i[0] for i in list_serial_ports()]

    def update_ports(self):
        ports = [i[0] for i in list_serial_ports()]
        message = self.extensionInstance.message_template()
        message["payload"]["content"] = {
            "ports": ports,
        }
        self.extensionInstance.publish(message)
        return "ok"

    def write(self, content):
        if self.ser:
            self.ser.write(content.encode('utf-8'))
            return "ok"

    def readline(self):
        if self.ser:
            content = self.ser.readline()  # timeout
            if content:
                content_str = content.decode()
                return content_str.strip()


class SerialExtension(Extension):

    NODE_ID = "eim/extension_uart_adapter"
    HELP_URL = "http://adapter.codelab.club/extension_guide/serial_adapter/"
    VERSION = "1.0"  # extension version
    DESCRIPTION = "serial adapter"

    def __init__(self):
        super().__init__()
        self.serialHelper = serialHelper(self)

    def run_python_code(self, code):
        # fork from python extension
        try:
            output = eval(code, {"__builtins__": None}, {
                "serialHelper": self.serialHelper,
            })
        except Exception as e:
            output = str(e)
        return output

    def extension_message_handle(self, topic, payload):
        self.logger.info(f'python code: {payload["content"]}')
        message_id = payload.get("message_id")
        python_code = payload["content"]
        output = self.run_python_code(python_code)
        payload["content"] = output
        message = {"payload": payload}  # 无论是否有message_id都返回
        self.publish(message)

    def run(self):
        "避免插件结束退出"
        while self._running:
            time.sleep(0.5)


export = SerialExtension