import time
from loguru import logger
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import get_or_create_node_logger_dir

# log for debug
node_logger_dir = get_or_create_node_logger_dir()
debug_log = str(node_logger_dir / "debug.log")
logger.add(debug_log, rotation="1 MB", level="DEBUG")


class EIMNode(AdapterNode):
    NODE_ID = "eim"
    
    def __init__(self):
        super().__init__(logger=logger)

    def _response_message_to_scratch(self, content, payload):
        message = self.message_template()
        message["payload"]["content"] = content
        message["payload"]["message_id"] = payload.get('message_id')
        self.publish(message)

    def extension_message_handle(self, topic, payload):
        self.logger.info(f'receive message from scratch, topic: {topic} payload: {payload}')
        content = payload["content"]
        if type(content) == str:
            content_send_to_scratch = content[::-1]  # 反转字符串
            self._response_message_to_scratch(content_send_to_scratch, payload)

    def run(self):
        i = 0
        while self._running:
            message = self.message_template()
            message["payload"]["content"] = str(i)
            self.publish(message)
            time.sleep(1)
            i += 1


if __name__ == "__main__":
    try:
        node = EIMNode()
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        # node.logger.debug("KeyboardInterrupt") # work mac
        if node._running:
            node.terminate()  # Clean up before exiting.
