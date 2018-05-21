'''
EIM: Everything Is Message
'''
import time
import threading

from scratch3_adapter import settings
from scratch3_adapter.core_extension import Extension

class EIMExtension(Extension):
    def __init__(self):
        name = type(self).__name__ # class name
        super().__init__(name)

    def run(self):
        # run 会被作为线程调用
        def message_monitor():
            message = self.read() # json
            # self.logger.debug("message_monitor:%s",str(message))
            if message["topic"] == "eim":
                self.logger.debug("eim message:%s",message["data"])
            time.sleep(1)
        bg_task = threading.Thread(target=message_monitor)
        self.logger.info("thread start")
        bg_task.daemon = True
        bg_task.start()
        while True:
            if settings.DEBUG:
                message = {"topic":"eim","message":"message"}
                self.publish(message)
                time.sleep(1)

export = EIMExtension