import time
from codelab_adapter.core_extension import Extension


class SyncHelloWorldExtension(Extension):
    def __init__(self):
        super().__init__()
        self.EXTENSION_ID = "eim"

    def send_message_to_scratch(self, payload):
        message = self.message_template()
        message["payload"] = payload
        self.publish(message)

    def extension_message_handle(self, topic, payload):
        self.logger.info(f'the message payload from scratch: {payload}')
        content = payload["content"]
        if type(content) == str:
            content_send_to_scratch = content[::-1] # 反转字符串
            time.sleep(1)
            payload["content"] = content_send_to_scratch
            self.send_message_to_scratch(payload)

    def run(self):
        while self._running:
            time.sleep(1)

export = SyncHelloWorldExtension
