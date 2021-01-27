'''
python -m serial.tools.miniterm <port_name> -h
python -m serial.tools.list_ports

todo
    parity 启用奇偶校验
'''

import time
# from codelab_adapter.uart_adapter import serialHelper
from codelab_adapter.core_extension import Extension

import serial
from serial.tools.list_ports import comports as list_serial_ports


class serialHelper:
    def __init__(self, extensionInstance):
        self.extensionInstance = extensionInstance
        self.logger = extensionInstance.logger
        self.port = None  # 当前连接的port
        self.ser = None

    def connect(self, port, **kwargs):
        self.logger.debug(f"args: {kwargs}")
        if self.ser:
            self.ser.close()
        # 默认支持 microbit, timeout 默认不超过scratch的积木 5s (4.5)
        if not kwargs.get("baudrate", None):
            kwargs["baudrate"] = 115200
        if not kwargs.get("timeout", None):
            kwargs["timeout"] = 4.5

        self.ser = serial.Serial(port, **kwargs)
        if self.ser.name:
            return "ok"

    def disconnect(self, **kwargs):
        if self.ser:
            self.ser.close()
            self.extensionInstance.pub_notification("设备已断开")
            return "ok"
        else:
            self.extensionInstance.pub_notification("未发现可用设备", type="ERROR")


    def list_ports(self):
        return [i[0] for i in list_serial_ports()]
        # return [port for port in ports if "VID:PID=0D28:0204" in port[2].upper()]

    # scan message type
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
            try:
                self.ser.write(content.encode('utf-8'))
                return "ok"
            except Exception as e:
                self.extensionInstance.logger.error(e)
                self.extensionInstance.pub_notification(str(e), type="ERROR")
                self.extensionInstance.terminate()
        else:
            self.extensionInstance.pub_notification(
                "未发现可用设备", type="ERROR")
            self.extensionInstance.terminate()

    def readline(self):
        if self.ser:
            try:
                content = self.ser.readline()  # todo timeout
                if content:
                    content_str = content.decode()
                    return content_str.strip()
            except Exception as e:
                self.extensionInstance.logger.error(e)
                self.extensionInstance.pub_notification(str(e), type="ERROR")
                self.extensionInstance.terminate()
        else:
            self.extensionInstance.pub_notification(
                "未发现可用设备", type="ERROR")
            self.extensionInstance.terminate()


class SerialExtension(Extension):

    NODE_ID = "eim/extension_uart_adapter"
    HELP_URL = "http://adapter.codelab.club/extension_guide/serial_adapter/"
    VERSION = "1.0"  # extension version
    DESCRIPTION = "serial adapter"
    WEIGHT = 93

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.serialHelper = serialHelper(self)

    def run_python_code(self, code):
        # fork from python extension
        try:
            output = eval(code, {"__builtins__": None}, {
                "serialHelper": self.serialHelper,
            })
        except Exception as e:
            self.logger.error(e)
            output = str(e)
            self.pub_notification(output, type="ERROR")
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