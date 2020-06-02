'''
usage:
    python cozmo_server.py

ref:
    https://github.com/anki/cozmo-python-sdk/blob/master/examples/apps/remote_control_cozmo.py#L335
'''
import queue
import time
import importlib
from loguru import logger

from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import get_or_create_node_logger_dir, install_requirement

# log for debug
node_logger_dir = get_or_create_node_logger_dir()
debug_log = str(node_logger_dir / "debug.log")
logger.add(debug_log, rotation="1 MB", level="DEBUG")


class CozmoNode(AdapterNode):
    NODE_ID = "eim/node_cozmo"
    WEIGHT = 100
    HELP_URL = "https://adapter.codelab.club/extension_guide/cozmo/"
    VERSION = "1.2.1"
    DESCRIPTION = "最好的 AI 教育机器人之一"
    REQUIREMENTS = ["cozmo"]

    def __init__(self):
        super().__init__(logger=logger)
        self.q = queue.Queue()

    def _import_requirement_or_import(self):
        requirement = self.REQUIREMENTS
        try:
            importlib.import_module("cozmo")
        except ModuleNotFoundError:
            self.pub_notification(f'try to install {" ".join(requirement)}...')
            install_requirement(requirement)
            self.pub_notification(f'{" ".join(requirement)} installed!')
        importlib.import_module("cozmo")
        import cozmo
        from cozmo.util import degrees, distance_mm, speed_mmps
        global cozmo, degrees, distance_mm, speed_mmps # make it global

    def extension_message_handle(self, topic, payload):
        self.q.put(payload)

    def exit_message_handle(self, topic, payload):
        self.terminate()

    def pub_event(self, event_name, event_param=""):
        message = self.message_template()
        message["payload"]["message_type"] = "device_event"
        message["payload"]["content"] = {
            "event_name": event_name,
            "event_param": event_param
        }
        self.publish(message)

    def onObjectTapped(self, evt, obj, **kwargs):
        # 事件数量巨大
        object_id = obj.object_id
        self.logger.debug(object_id)
        event_name = "ObjectTapped"
        event_param = object_id
        self.pub_event(event_name, event_param)

    def onObjectObserved(self, evt, obj, **kwargs):
        object_id = obj.object_id
        event_param = object_id
        event_name = "ObjectObserved"
        self.pub_event(event_name, event_param)

    def onObjectAppeared(self, evt, obj, **kwargs):
        object_id = obj.object_id
        event_param = object_id
        event_name = "ObjectAppeared"
        self.pub_event(event_name, event_param)

    def onObjectDisappeared(self, evt, obj, **kwargs):
        object_id = obj.object_id
        event_param = object_id
        event_name = "ObjectDisappeared"
        self.pub_event(event_name, event_param)

    def onObjectMovingStarted(self, evt, obj, **kwargs):
        object_id = obj.object_id
        event_param = object_id
        event_name = "ObjectMovingStarted"
        self.pub_event(event_name, event_param)

    # face
    def onFaceAppeared(self, evt, face, **kwargs):
        event_name = "FaceAppeared"
        self.logger.debug(face.name)
        self.logger.debug(face.known_expression)
        event_param = face.known_expression
        self.pub_event(event_name, event_param)

    def onFaceObserved(self, evt, face, **kwargs):
        # expression -> FACIAL_EXPRESSION_HAPPY("happy")
        event_name = "FaceObserved"
        self.logger.debug(face.name)
        self.logger.debug(face.known_expression)
        event_param = face.known_expression
        self.logger.debug(
            f'face name -> {face.name}, face expression -> {face.known_expression}'
        )
        if event_param:
            self.pub_event(event_name, event_param)

    def onFaceDisappeared(self, evt, face, **kwargs):
        event_name = "FaceDisappeared"
        event_param = face.known_expression
        self.pub_event(event_name, event_param)

    # pets
    def onPetAppeared(self, evt, pet, **kwargs):
        # 与face机制不一致
        self.logger.debug("PetAppeared")
        self.logger.debug(pet.pet_type)
        event_name = "PetAppeared"
        event_param = pet.pet_type
        self.pub_event(event_name, event_param)

    def onPetObserved(self, evt, pet, **kwargs):
        self.logger.debug("PetObserved")
        self.logger.debug(pet.pet_type)
        event_name = "PetObserved"
        event_param = pet.pet_type
        self.pub_event(event_name, event_param)

    def onPetDisappeared(self, evt, pet, **kwargs):
        self.logger.debug("PetDisappeared")
        self.logger.debug(pet.pet_type)
        event_name = "PetDisappeared"
        event_param = pet.pet_type
        self.pub_event(event_name, event_param)

    def onRobotObservedMotion(self, evt, **kwargs):
        event_name = "RobotObservedMotion"  # EvtRobotObservedMotion
        logger.debug(event_name)
        self.pub_event(event_name)

    def cozmo_program(self, robot):
        '''
        event
            cozmo.faces.EvtFaceAppeared
            cozmo.camera.EvtRobotObservedMotion
            cozmo.world.EvtNewCameraImage
        '''
        # Object
        robot.add_event_handler(cozmo.objects.EvtObjectTapped,
                                self.onObjectTapped)
        # ObjectObserved 发送频率非常高 会导致冲刷缓存变量(todo 优化 js extension 消息接收机制)
        # robot.add_event_handler(cozmo.objects.EvtObjectObserved, self.onObjectObserved)

        robot.add_event_handler(cozmo.objects.EvtObjectAppeared,
                                self.onObjectAppeared)
        robot.add_event_handler(cozmo.objects.EvtObjectDisappeared,
                                self.onObjectDisappeared)
        robot.add_event_handler(cozmo.objects.EvtObjectMovingStarted,
                                self.onObjectMovingStarted)

        # face
        robot.add_event_handler(cozmo.faces.EvtFaceAppeared,
                                self.onFaceAppeared)
        robot.add_event_handler(cozmo.faces.EvtFaceObserved,
                                self.onFaceObserved)
        robot.add_event_handler(cozmo.faces.EvtFaceDisappeared,
                                self.onFaceDisappeared)

        # pets
        robot.add_event_handler(cozmo.pets.EvtPetAppeared, self.onPetAppeared)
        robot.add_event_handler(cozmo.pets.EvtPetDisappeared,
                                self.onPetDisappeared)
        # robot.add_event_handler(cozmo.pets.EvtPetObserved, self.onPetObserved)

        # world Camera
        # robot.add_event_handler(cozmo.camera.EvtRobotObservedMotion, self.onRobotObservedMotion)

        self.pub_notification("Cozmo Connected!", type="SUCCESS")
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
                    self.pub_notification(str(e), type="ERROR")
                payload["content"] = str(output)
                message = {"payload": payload}
                self.publish(message)

    def run(self):
        self._import_requirement_or_import()
        cozmo.run_program(self.cozmo_program)


if __name__ == "__main__":
    try:
        node = CozmoNode()
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        node.terminate()  # Clean up before exiting
    except Exception as e:
        node.logger.error(str(e))
        node.pub_notification(str(e), type="ERROR")
        time.sleep(0.05)
        node.terminate()  # Clean up before exiting.
