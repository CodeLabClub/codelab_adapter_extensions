import time

from codelab_adapter.core_extension import Extension
from codelab_adapter.microbit_helper import MicrobitRadioHelper
'''
todo 错误信息报告 通知
'''


class MicrobitRadioProxy(Extension):
    '''
    use TokenBucket to limit message rate(pub) https://github.com/CodeLabClub/codelab_adapter_client_python/blob/master/codelab_adapter_client/utils.py#L25
    '''

    NODE_ID = "eim/extension_microbit_radio"
    HELP_URL = "http://adapter.codelab.club/extension_guide/microbit_radio/"
    WEIGHT = 98
    VERSION = "1.1"  # 简化makecode对字符串的处理，移除\r
    DESCRIPTION = "Microbit radio 信号中转站"

    def __init__(self, **kwargs):  # kwargs 接受启动参数
        super().__init__(
            bucket_token=200,  #  默认是100条 hub模式消息量大
            bucket_fill_rate=100,
            **kwargs)
        self.microbitHelper = MicrobitRadioHelper(self)

    def run_python_code(self, code):
        # fork from python extension
        try:
            output = eval(code, {"__builtins__": None}, {
                "microbitHelper": self.microbitHelper,
            })
        except Exception as e:
            output = str(e)
            # 也作为提醒
            self.pub_notification(output, type="ERROR")
        return output

    def extension_message_handle(self, topic, payload):
        '''
            test: codelab-message-pub -j '{"topic":"scratch/extensions/command","payload":{"node_id":"eim/extension_microbit_radio", "content":"microbitHelper.write(\"c\")"}}'
        '''
        self.logger.info(f'python code: {payload["content"]}')
        message_id = payload.get("message_id")
        python_code = payload["content"]
        if "microbitHelper" in python_code:
            output = self.run_python_code(python_code)
            payload["content"] = output
            message = {"payload": payload}  # 无论是否有message_id都返回
            self.publish(message)

    def run(self):
        while self._running:
            if self.microbitHelper.ser:
                # node -> microbit adapter
                response_from_microbit = self.microbitHelper.get_response_from_microbit(
                )
                # print(response_from_microbit)
                if response_from_microbit:
                    print(response_from_microbit)
                    message = self.message_template()
                    message["payload"]["content"] = response_from_microbit
                    self.publish(message)
            else:
                time.sleep(0.5)
                # 广播不在线


export = MicrobitRadioProxy
