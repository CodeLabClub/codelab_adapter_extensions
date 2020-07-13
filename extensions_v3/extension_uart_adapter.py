import time
from codelab_adapter.uart_adapter import serialHelper
from codelab_adapter.core_extension import Extension

class SerialExtension(Extension):

    NODE_ID = "eim/extension_uart_adapter"
    HELP_URL = "http://adapter.codelab.club/extension_guide/serial_adapter/"
    VERSION = "1.0"  # extension version
    DESCRIPTION = "serial adapter"
    WEIGHT = 93

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