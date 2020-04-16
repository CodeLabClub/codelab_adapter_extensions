'''
usage:
    python cozmo_server.py

ref:
    https://github.com/anki/cozmo-python-sdk/blob/master/examples/apps/remote_control_cozmo.py#L335
'''
import time
import queue
import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps

from codelab_adapter_client import AdapterNode


class CozmoNode(AdapterNode):
    def __init__(self):
        super().__init__()
        self.NODE_ID = self.generate_node_id(__file__)
        self.HELP_URL = "https://adapter.codelab.club/extension_guide/cozmo/"
        self.q = queue.Queue()

    def extension_message_handle(self, topic, payload):
        self.q.put(payload)

    def exit_message_handle(self, topic, payload):
        self.terminate()

    def cozmo_program(self, robot):
        self.pub_notification("Vector Connected!", type="SUCCESS")
        while self._running:
            time.sleep(0.05)
            if not self.q.empty():
                payload = self.q.get()
                self.logger.info(f'python: {payload}')
                message_id = payload.get("message_id")
                python_code = payload["content"]

                try:
                    output = eval(python_code, {"__builtins__": None}, {
                        "cozmo": cozmo,
                        "robot": robot
                    })
                except Exception as e:
                    output = e
                payload["content"] = str(output)
                message = {"payload": payload}
                self.publish(message)

    def run(self):
        cozmo.run_program(self.cozmo_program)


if __name__ == "__main__":
    try:
        node = CozmoNode()
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        node.terminate()  # Clean up before exiting.s
    except Exception as e:
        node.logger.error(str(e))
        node.pub_notification(str(e), type="ERROR")
        time.sleep(0.05)
        node.terminate()  # Clean up before exiting.