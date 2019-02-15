'''
EIM: Everything Is Message
'''
import time
import threading

from codelab_adapter import settings
from codelab_adapter.core_extension import Extension


class EIMExtension(Extension):
    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)
        self.TOPIC = "eim"

    def run(self):
        '''
        run 会被作为线程调用
        当前插件功能:
            往scratch不断发送信息
        '''

        def message_monitor():
            while True:
                read_message = self.read()  # json
                self.logger.info("eim message:%s", str(read_message))
                topic = read_message.get("topic")
                if topic == self.TOPIC:
                    data = read_message.get("payload")
                    self.logger.info(
                        "eim message:%s",
                        data)  # for developer debug : tail info.log

        bg_task = threading.Thread(target=message_monitor)
        self.logger.info("thread start")
        bg_task.daemon = True
        bg_task.start()

        while self._running:
            message = {"topic": self.TOPIC, "payload": "payload"}
            self.publish(message)
            time.sleep(1)


export = EIMExtension