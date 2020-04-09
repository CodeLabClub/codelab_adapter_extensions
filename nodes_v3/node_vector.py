'''
# python >= 3.6
pip3 install codelab_adapter_client anki_vector --user
wget https://github.com/anki/vector-python-sdk/raw/master/examples/tutorials/01_hello_world.py
python3 01_hello_world.py  # should be ok
'''

import anki_vector
import queue
import time

from codelab_adapter_client import AdapterNode

class VectorNode(AdapterNode):
    '''
    Everything Is Message
    ref: https://github.com/CodeLabClub/codelab_adapter_extensions/blob/master/extensions_v2/extension_python_kernel.py
    
    node pub it's status: pid
    '''

    def __init__(self):
        super().__init__()
        self.EXTENSION_ID = "eim/vector"  # default: eim
        self.HELP_URL = "https://adapter.codelab.club/extension_guide/vector/"
        self.q = queue.Queue()
        # from_jupyter/extensions

    def extension_message_handle(self, topic, payload):
        self.q.put(payload)

    # exit_message_handle 只是node需要 self.ternimate()
    def exit_message_handle(self, topic, payload):
        self.terminate()


    def run(self):
        with anki_vector.Robot() as robot:
            self.pub_notification("Vector Connected!", type="SUCCESS")
            while self._running:
                time.sleep(0.05)
                if not self.q.empty():
                    payload = self.q.get()
                    self.logger.info(f'python: {payload}')
                    message_id = payload.get("message_id")
                    python_code = payload["content"]

                    try:
                        # 为了安全性, 做一些能力的牺牲, 放弃使用exec
                        output = eval(python_code, {"__builtins__": None}, {
                            "anki_vector": anki_vector,
                            "robot": robot
                        })
                    except Exception as e:
                        output = e
                    payload["content"] = str(output)
                    message = {"payload": payload}
                    self.publish(message)
                

if __name__ == "__main__":
    try:
        node = VectorNode()
        node.receive_loop_as_thread(
        )  # run extension_message_handle, noblock(threaded)
        node.run()
    except KeyboardInterrupt:
        node.terminate()  # Clean up before exiting.s
    except Exception as e:
        node.logger.error(str(e))
        node.pub_notification(str(e), type="ERROR")
        time.sleep(0.05)
        node.terminate()  # Clean up before exiting.