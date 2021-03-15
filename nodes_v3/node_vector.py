'''
# python >= 3.6
pip3 install codelab_adapter_client anki_vector --user
wget https://github.com/anki/vector-python-sdk/raw/master/examples/tutorials/01_hello_world.py
python3 01_hello_world.py  # should be ok
'''

import os
import queue
import time

from loguru import logger
import anki_vector  # 需要手动配置，就不自动安装了

from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import get_or_create_node_logger_dir

# log for debug
node_logger_dir = get_or_create_node_logger_dir()
debug_log = str(node_logger_dir / "debug.log")
logger.add(debug_log, rotation="1 MB", level="DEBUG")


class VectorNode(AdapterNode):
    '''
    Everything Is Message
    ref: https://github.com/CodeLabClub/codelab_adapter_extensions/blob/master/extensions_v2/extension_python_kernel.py
    
    node pub it's status: pid
    '''

    NODE_ID = "eim/node_vector"  # 手写, 没有魔法
    WEIGHT = 99
    HELP_URL = "https://adapter.codelab.club/extension_guide/vector/"
    VERSION = "1.0.0"
    DESCRIPTION = "最好的 AI 教育机器人之一， Cozmo的下一代"

    def __init__(self, **kwargs):
        super().__init__(logger=logger, **kwargs)  # todo log
        # self.NODE_ID = self.generate_node_id(__file__) # 检查时发现
        self.q = queue.Queue()
        # from_jupyter/extensions

    def extension_message_handle(self, topic, payload):
        self.q.put(payload)

    def pub_event(self, event_name, event_param=""):
        message = self.message_template()
        message["payload"]["message_type"] = "device_event"
        message["payload"]["content"] = {
            "event_name": event_name,
            "event_param": event_param
        }
        self.publish(message)

    def handle_object_appeared(self, robot, event_type, event):
        # This will be called whenever an EvtObjectAppeared is dispatched -
        # whenever an Object comes into view.
        # print(f"--------- Vector started seeing an object --------- \n{event.obj}")
        object_id = event.obj.object_id
        event_param = object_id
        event_name = "ObjectAppeared"
        self.pub_event(event_name, event_param)

    def handle_object_disappeared(self, robot, event_type, event):
        # This will be called whenever an EvtObjectDisappeared is dispatched -
        # whenever an Object goes out of view.
        object_id = event.obj.object_id
        event_param = object_id
        event_name = "ObjectDisappeared"
        self.pub_event(event_name, event_param)

    def handle_object_tapped(self, robot, event_type, event):
        # This will be called whenever an EvtObjectDisappeared is dispatched -
        # whenever an Object goes out of view.
        print("ObjectTapped")
        object_id = event.obj.object_id
        event_param = object_id
        event_name = "ObjectTapped"
        self.pub_event(event_name, event_param)

    def handle_object_moved(self, robot, event_type, event):
        # This will be called whenever an EvtObjectDisappeared is dispatched -
        # whenever an Object goes out of view.
        object_id = event.obj.object_id
        event_param = object_id
        event_name = "ObjectMovingStarted"
        self.pub_event(event_name, event_param)


    '''
    def handle_face_appeared(self, robot, event_type, event):
        print(f"--------- Vector observed an face --------- \\n{event.face}")

    def handle_face_disappeared(self, robot, event_type, event):
        # This will be called whenever an EvtFaceDisappeared is dispatched -
        # whenever an face goes out of view.
        print(
            f"--------- Vector stopped seeing an face --------- \\n{event.face}"
        )
    '''

    def run(self):
        # enable_face_detection = True, show_viewer=True  https://github.com/anki/vector-python-sdk/blob/8ea77411dc56b16039b802e7c60c25a6475dcf8b/anki_vector/faces.py#L165
        with anki_vector.Robot() as robot:
            # with 以内 vector 错误无法被捕获，sdk做了特殊处理
            self.pub_notification("Vector 已连接", type="SUCCESS")

            # event
            ## object event

            robot.events.subscribe(self.handle_object_appeared,
                                   anki_vector.events.Events.object_appeared)
            robot.events.subscribe(
                self.handle_object_disappeared,
                anki_vector.events.Events.object_disappeared)
            '''
            robot.events.subscribe(self.handle_object_tapped,
                                   anki_vector.events.Events.object_tapped)
            robot.events.subscribe(self.handle_object_moved,
                                   anki_vector.events.Events.object_moved)
            '''
            ## face
            '''
            robot.events.subscribe(self.handle_face_appeared,
                                   anki_vector.events.Events.face_appeared)
            robot.events.subscribe(self.handle_face_disappeared,
                                   anki_vector.events.Events.face_disappeared)
            '''

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
                        self.pub_notification(str(e), type="ERROR")
                    payload["content"] = str(output)
                    message = {"payload": payload}
                    self.publish(message)


def main(**kwargs):
    try:
        node = VectorNode(**kwargs)
        node.receive_loop_as_thread(
        )  # run extension_message_handle, noblock(threaded)
        node.run()
    except KeyboardInterrupt:
        # 依赖这个退出
        if node._running:
            node.terminate()  # Clean up before exiting.s
    except Exception as e:
        node.logger.error(str(e))  # 为何是空？
        # node.pub_notification(str(e), type="ERROR")
        if node._running:
            node.terminate()  # Clean up before exiting.


if __name__ == "__main__":
    main()