import time
import threading

from codelab_adapter import settings
from codelab_adapter.core_extension import Extension


class ReqRepExtension(Extension):
    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)
        self.TOPIC = "eim/reqRep"

    def run(self):
        while self._running:
            read_message = self.read()
            topic = read_message.get('topic')
            if topic == self.TOPIC:
                self.logger.info(str(read_message))
                time.sleep(1)
                content = read_message.get('content')
                read_message['content'] = content[::-1]
                self.publish(read_message)
                # time.sleep(1)


export = ReqRepExtension
