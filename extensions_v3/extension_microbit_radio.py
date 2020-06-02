import serial
import time
import json
import queue

from codelab_adapter.utils import find_microbit
from codelab_adapter.core_extension import Extension


def check_env():
    return find_microbit()


class MicrobitRadioProxy(Extension):
    '''
    use TokenBucket to limit message rate(pub) https://github.com/CodeLabClub/codelab_adapter_client_python/blob/master/codelab_adapter_client/utils.py#L25
    '''
    
    NODE_ID = "eim/extension_microbit_radio"
    HELP_URL = "http://adapter.codelab.club/extension_guide/microbit_radio/"
    WEIGHT = 98
    VERSION = "1.0"  # extension version
    DESCRIPTION = "Microbit radio 信号中继"

    def __init__(self, bucket_token=20, bucket_fill_rate=10):
        super().__init__(bucket_token=bucket_token, bucket_fill_rate=bucket_fill_rate)

        self.q = queue.Queue()

    def extension_message_handle(self, topic, payload):
        '''
            test: codelab-message-pub -j '{"topic":"scratch/extensions/command","payload":{"node_id":"eim/usbMicrobit", "content":"display.show(\"c\")"}}'
            '''
        # self.q.put(payload)
        content = payload["content"] + "\r\n"
        self.ser.write(content.encode('utf-8'))

    def run(self):
        while self._running:
            env_is_valid = check_env()
            # 等待用户连接microbit
            if not env_is_valid:
                self.logger.info("错误信息: %s", "请插入microbit")
                self.pub_notification("请插入microbit", type="ERROR")
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
                rate = 20  # todo: bucket token
                time.sleep(1 / rate)


export = MicrobitRadioProxy
