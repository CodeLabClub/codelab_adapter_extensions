import serial
import time
import json
import threading

from codelab_adapter.utils import find_microbit, ui_error
from codelab_adapter.core_extension import Extension


def check_env():
    return find_microbit()
    # 环境是否满足要求


class UsbMicrobitProxy(Extension):
    def __init__(self):
        name = type(self).__name__
        super().__init__(name)
        self.scratch3_message = {}
        self.TOPIC = "eim/usbMicrobit" # 不再使用ROS风格

    def run(self):
        while self._running:
            env_is_valid = check_env()
            # 等待用户连接microbit
            if not env_is_valid:
                self.logger.info("错误信息: %s", "请插入microbit")
                ui_error("错误信息", "请插入microbit")
                time.sleep(5)
            else:
                port = find_microbit()
                self.ser = serial.Serial(port, 115200, timeout=1)
                break

        def get_response_from_microbit():
            try:
                data = self.ser.readline()
                # self.logger.info("in response")
                if data:
                    data = data.decode()
                    try:
                        data = eval(data)
                    except (ValueError, SyntaxError):
                        pass
                    else:
                        # self.logger.info(data)
                        return data
            except UnicodeDecodeError:
                pass
            return None

        lock = threading.Lock()

        def request():
            while self._running:
                lock.acquire()
                self.scratch3_message = self.read()
                lock.release()

        bg_task = threading.Thread(target=request)
        self.logger.debug("thread start")
        bg_task.daemon = True
        bg_task.start()

        while self._running:
            # 一读一写 比较稳定
            scratch3_message = self.scratch3_message
            self.logger.debug("scratch3_message {}".format(scratch3_message))
            self.scratch3_message = {}
            if scratch3_message == {}:
                scratch3_message = {"topic": self.TOPIC, "data": ""}
            scratch3_message = json.dumps(scratch3_message) + "\r\n"
            scratch3_message_bytes = scratch3_message.encode('utf-8')
            self.logger.debug(scratch3_message_bytes)
            self.ser.write(scratch3_message_bytes)
            # response
            response_from_microbit = get_response_from_microbit()
            if response_from_microbit:
                # message = {"topic":self.TOPIC, "data":} # todo 不要在microbit中构建消息
                self.publish(response_from_microbit) 
                time.sleep(0.05)


export = UsbMicrobitProxy
