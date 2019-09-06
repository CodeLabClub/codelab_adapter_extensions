import serial
import time
import json
import queue

from codelab_adapter.utils import find_microbit
from codelab_adapter.core_extension import Extension

def check_env():
    return find_microbit()
    # 环境是否满足要求


class UsbMicrobitProxy(Extension):
    def __init__(self):
        name = type(self).__name__
        super().__init__(name)
        self.EXTENSION_ID = "eim/usbMicrobit"
        self.q = queue.Queue()

    def extension_message_handle(self, topic, payload):
        self.q.put(payload)

    def run(self):
        while self._running:
            env_is_valid = check_env()
            # 等待用户连接microbit
            if not env_is_valid:
                self.logger.info("错误信息: %s", "请插入microbit")
                self.pub_notification("请插入microbit")
                time.sleep(5)
            else:
                port = find_microbit()
                self.ser = serial.Serial(port, 115200, timeout=1)
                break

        def get_response_from_microbit():
            try:
                data = self.ser.readline()
                if data:
                    data = data.decode()
                    try:
                        data = eval(data)
                    except (ValueError, SyntaxError):
                        pass
                    else:
                        return data
            except UnicodeDecodeError:
                pass
            return None

        while self._running:
            # 一读一写 比较稳定
            try:
                if not self.q.empty():
                    payload = self.q.get()
                    message_id = payload.get("message_id")
                    scratch3_message = {"topic": self.EXTENSION_ID, "payload": ""}
                    scratch3_message["payload"] = payload["content"]
                else:
                    message_id = ""
                    scratch3_message = {"topic": self.EXTENSION_ID, "payload": ""}
                scratch3_message = json.dumps(scratch3_message) + "\r\n"
                scratch3_message_bytes = scratch3_message.encode('utf-8')
                self.logger.debug(scratch3_message_bytes)
                self.ser.write(scratch3_message_bytes)
                # response
                response_from_microbit = get_response_from_microbit()
                if response_from_microbit:
                    message = {"payload": {"content": response_from_microbit["payload"]}}
                    if message_id:
                        message["payload"]["message_id"] = message_id
                    self.publish(message)
            except:
                try:
                    port = find_microbit()
                    self.ser = serial.Serial(port, 115200, timeout=1)
                except:
                    pass
            finally:
                rate = 10
                time.sleep(1/rate)


export = UsbMicrobitProxy
