import time
import random
from codelab_adapter.core_extension import Extension


class RobotXYExtension(Extension):
    def __init__(self):
        super().__init__()
        self.EXTENSION_ID = "eim/robot"

    def extension_message_handle(self, topic, payload):
        self.logger.debug(f'the message payload from scratch: {payload}')
        content = payload["content"]
        if type(content) == dict:
            x = content["x"]
            y = content["y"]
            self.logger.info(f'x:{x}; y:{y}')

    def run(self):
        while self._running:
            message = self.message_template()
            random_x = random.randint(-240,240)
            random_y = random.randint(-180,180)
            message["payload"]["content"] = {"x":random_x, "y":random_y}
            self.publish(message)
            time.sleep(1)

export = RobotXYExtension
