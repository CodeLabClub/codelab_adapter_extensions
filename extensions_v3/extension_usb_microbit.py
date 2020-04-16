import serial
import time
import json
import queue

from codelab_adapter.utils import find_microbit
from codelab_adapter.core_extension import Extension
'''
todo:
    使用makecode构建固件
        command
        query
        event
'''


def check_env():
    # 检查环境是否满足要求。 todo: 处理多个microbit的情况
    return find_microbit()


class UsbMicrobitProxy(Extension):
    '''
    use TokenBucket to limit message rate(pub) https://github.com/CodeLabClub/codelab_adapter_client_python/blob/master/codelab_adapter_client/utils.py#L25
    '''
    HELP_URL = "http://adapter.codelab.club/extension_guide/microbit/"
    WEIGHT = 99
    
    def __init__(self, bucket_token=20, bucket_fill_rate=10):
        super().__init__(bucket_token=bucket_token,
                         bucket_fill_rate=bucket_fill_rate)
        self.NODE_ID = self.generate_node_id(__file__)

        self.q = queue.Queue()

    def extension_message_handle(self, topic, payload):
        '''
            test: codelab-message-pub -j '{"topic":"scratch/extensions/command","payload":{"node_id":"eim/usbMicrobit", "content":"display.show(\"c\")"}}'
            '''
        self.q.put(payload)

    def run(self):
        while self._running:
            env_is_valid = check_env()
            # 等待用户连接microbit
            # todo: 由前端选择 jupyter stdin channel
            if not env_is_valid:
                self.logger.error("No micro:bit found")
                self.pub_notification("No micro:bit found",
                                      type="ERROR")  # todo 针对node_id的提醒
                time.sleep(5)
            else:
                port = find_microbit()
                self.ser = serial.Serial(port, 115200, timeout=1)
                break
        self.pub_notification("micro:bit Connected!", type="SUCCESS")

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
            # 一读一写 比较稳定, todo: CQRS , todo makecode create hex
            try:
                if not self.q.empty():
                    payload = self.q.get()
                    message_id = payload.get("message_id")
                    scratch3_message = {
                        "topic": self.NODE_ID,
                        "payload": ""
                    }
                    scratch3_message["payload"] = payload["content"]
                else:
                    message_id = ""
                    scratch3_message = {
                        "topic": self.NODE_ID,
                        "payload": ""
                    }
                scratch3_message = json.dumps(scratch3_message) + "\r\n"
                scratch3_message_bytes = scratch3_message.encode('utf-8')
                self.logger.debug(scratch3_message_bytes)
                self.ser.write(scratch3_message_bytes)
                # response
                response_from_microbit = get_response_from_microbit()
                if response_from_microbit:
                    message = {
                        "payload": {
                            "content": response_from_microbit["payload"]
                        }
                    }
                    if message_id:
                        message["payload"]["message_id"] = message_id
                    self.publish(message)
            except:
                # todo: 错误信息不明确
                try:
                    port = find_microbit()
                    self.ser = serial.Serial(port, 115200, timeout=1)
                except:
                    pass
            finally:
                rate = 10
                time.sleep(1 / rate)


export = UsbMicrobitProxy
