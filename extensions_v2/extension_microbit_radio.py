import serial
import time
import json
import queue

from codelab_adapter.utils import find_microbit, TokenBucket
from codelab_adapter.core_extension import Extension


def check_env():
    return find_microbit()


class MicrobitRadioProxy(Extension):
    def __init__(self):
        name = type(self).__name__
        super().__init__(name)
        self.EXTENSION_ID = "eim/radioMicrobit"
        self.q = queue.Queue()
        self.bucket = TokenBucket(10, 5)  # rate limit

    def extension_message_handle(self, topic, payload):
        if self.bucket.consume(1):
            '''
            test: codelab-message-pub -j '{"topic":"scratch/extensions/command","payload":{"extension_id":"eim/usbMicrobit", "content":"display.show(\"c\")"}}'
            '''
            # self.q.put(payload)
            content = payload["content"] + "\r\n"
            self.ser.write(content.encode('utf-8'))
        else:
            self.logger.error(f"rate limit! {payload}")

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
            data = self.ser.readline()
            data_str = data.decode()
            return data_str.strip()

        while self._running:
            try:
                response_from_microbit = get_response_from_microbit()
                # print(response_from_microbit)
                if response_from_microbit:
                    print(response_from_microbit)
                    message = self.message_template()
                    message["payload"]["content"] = response_from_microbit
                    self.publish(message)
            except:
                try:
                    port = find_microbit()
                    self.ser = serial.Serial(port, 115200, timeout=1)
                except:
                    pass
            finally:
                rate = 20  # 多少帧合适 30?，传输数值需要注意
                time.sleep(1 / rate)


export = MicrobitRadioProxy
