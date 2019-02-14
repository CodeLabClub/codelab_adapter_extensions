import sys
sys.path.append("/usr/local/lib/python3.6/site-packages")
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

# base on eim
import time
import threading

from codelab_adapter import settings
from codelab_adapter.core_extension import Extension


class EIMExtension(Extension):
    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)
        self.init_chatbot()

    def init_chatbot(self):

        self.deepThought = ChatBot("deepThought", read_only=True)
        self.deepThought.set_trainer(ListTrainer)
        self.deepThought.train([
            "action",
            "嗳，渡边君，真喜欢我?",
            "那还用说",
            "那么，可依得我两件事?",
            "三件也依得",
        ])

    def run(self):
        while self._running:
            if settings.DEBUG:
                read_message = self.read()  # json
                # scratch user say
                # 同步模式 基于异步实现
                # self.logger.debug("message:%s", str(read_message))
                content = read_message["payload"]
                if read_message.get("topic") == "eim":
                    # 由前端发起 action
                    self.logger.info("eim message:%s", content)
                    response = self.deepThought.get_response(content).text
                    message = {"topic": "eim", "payload": response}
                    self.publish(message)
                # time.sleep(1)

export = EIMExtension
