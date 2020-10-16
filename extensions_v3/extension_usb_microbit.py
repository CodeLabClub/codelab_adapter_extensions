import queue
import time

from codelab_adapter.microbit_helper import UsbMicrobitHelper
from codelab_adapter.core_extension import Extension
'''
todo:
    使用makecode构建固件
        command
        query
        event
'''


class UsbMicrobitProxy(Extension):
    '''
    use TokenBucket to limit message rate(pub) https://github.com/CodeLabClub/codelab_adapter_client_python/blob/master/codelab_adapter_client/utils.py#L25
    '''

    NODE_ID = "eim/extension_usb_microbit"
    HELP_URL = "http://adapter.codelab.club/extension_guide/microbit/"
    WEIGHT = 99
    DESCRIPTION = "使用 Microbit， 为物理世界编程"

    def __init__(self, bucket_token=20, bucket_fill_rate=10, **kwargs):
        super().__init__(bucket_token=bucket_token,
                         bucket_fill_rate=bucket_fill_rate, **kwargs)
        self.microbitHelper = UsbMicrobitHelper(self)
        self.q = queue.Queue()

    def run_python_code(self, code):
        # fork from python extension
        try:
            output = eval(code, {"__builtins__": None}, {
                "microbitHelper": self.microbitHelper,
            })
        except Exception as e:
            output = str(e)
        return output

    def extension_message_handle(self, topic, payload):
        '''
            test: codelab-message-pub -j '{"topic":"scratch/extensions/command","payload":{"node_id":"eim/extension_usb_microbit", "content":"display.show(\"c\")"}}'
        '''
        self.logger.info(f'python code: {payload["content"]}')
        message_id = payload.get("message_id")
        python_code = payload["content"]
        if "microbitHelper" in python_code:
            output = self.run_python_code(python_code)
            payload["content"] = output
            message = {"payload": payload}  # 无论是否有message_id都返回
            self.publish(message)
        else:
            self.q.put(python_code) # 写入
            # todo 返回值
            payload["content"] = "ok"
            message = {"payload": payload}
            self.publish(message)

    def run(self):
        while self._running:
            # 写入才能读出
            # 检查是否打开
            if self.microbitHelper.ser:
                try:
                    self.microbitHelper.send_command()
                    # 一读一写 比较稳定, todo: CQRS , todo makecode create hex
                    response_from_microbit = self.microbitHelper.get_response_from_microbit(
                    )
                    if response_from_microbit:
                        message = self.message_template()
                        message["payload"]["content"] = response_from_microbit[
                            "payload"]
                        self.publish(message)
                    rate = 10
                    time.sleep(1 / rate)
                except Exception as e:
                    self.logger.debug(str(e))
                    time.sleep(0.5)
            else:
                time.sleep(0.5)


export = UsbMicrobitProxy
