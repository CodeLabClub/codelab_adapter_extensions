'''
usage:
    python cozmo_server.py

多台机器人
    https://github.com/anki/cozmo-python-sdk/blob/dd29edef18748fcd816550469195323842a7872e/examples/multi_robot/multi_robot_unified.py
    默认采用优先发现原则 https://github.com/anki/cozmo-python-sdk/blob/dd29edef18748fcd816550469195323842a7872e/src/cozmo/run.py#L400
ref:
    https://github.com/anki/cozmo-python-sdk/blob/master/examples/apps/remote_control_cozmo.py#L335

get status
    https://github.com/wwj718/calypso/blob/master/server.py#L353

调试
    https://github.com/anki/cozmo-python-sdk/blob/master/examples/apps/cli.py
'''
import queue
import json
import time

from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import install_requirement
from codelab_adapter_client.thing import AdapterThing
from codelab_adapter_client.utils import threaded

import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps, Pose
from codelab_adapter_client.config import settings
from loguru import logger
debug_log = str(settings.NODE_LOG_PATH / "cozmo.log")
logger.add(debug_log, rotation="1 MB", level="DEBUG")


class CozmoProxy(AdapterThing):
    def __init__(self, node_instance):
        super().__init__(thing_name="Cozmo", node_instance=node_instance)
        self.disconnect_flag = False

    def _say_hi(self, robot):
        # pass
        # robot.say_text("hi").wait_for_completed()
        pass

    def list(self, timeout=5) -> list:
        if self.thing:
            # 检查是否连接正常
            return ["Cozmo"]
        try:
            # message id返回
            cozmo.run_program(self._say_hi)  # 联通性测试！
            return ["Cozmo"]
        except:  # 不能加Exception 协程
            # cozmo 有问题？ 如果正常连接呢？
            # self.node_instance.logger.error()
            self.node_instance.pub_notification("未发现 Cozmo",
                                                type="ERROR")
            # self.node_instance.terminate()
            return []

    @threaded
    def _connect(self):
        # RuntimeError: This event loop is already running
        cozmo.run_program(self.cozmo_program)
        # todo 需要在主线程打开
        # cozmo.run_program(self.cozmo_program, use_3d_viewer=True, use_viewer=True)
        '''
        try:
              # 阻塞
        except:
            self.thing = None # ??
        '''
            
    def connect(self, ip, timeout=5):
        if self.thing:
            # 之前连过
            return
        self.is_connected = True
        self._connect()
        time.sleep(0.5)

    def status(self, **kwargs) -> bool:
        pass

    def disconnect(self):
        # self.node_instance
        self.node_instance.pub_notification(f'{self.node_instance.NODE_ID} 已断开', type="WARNING")
        if self.thing:
            try:
                self.thing.say_text("see you later").wait_for_completed()
            except Exception as e:
                self.node_instance.logger.error(str(e))
        self.thing = None
        self.is_connected = False
        self.disconnect_flag = True
        time.sleep(0.1)  # 等待检测
        self.disconnect_flag = False
        # self.node_instance.terminate()  # 断开 重复连接cozmo可能有问题
        
    #  业务
    def pub_event(self, event_name, event_param=""):
        message = self.node_instance.message_template()
        message["payload"]["message_type"] = "device_event"
        message["payload"]["content"] = {
            "event_name": event_name,
            "event_param": event_param
        }
        self.node_instance.publish(message)

    def onObjectTapped(self, evt, obj, **kwargs):
        # 事件数量巨大
        object_id = obj.object_id
        self.node_instance.logger.debug(object_id)
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
        self.node_instance.logger.debug(face.name)
        self.node_instance.logger.debug(face.known_expression)
        event_param = face.known_expression
        self.pub_event(event_name, event_param)

    def onFaceObserved(self, evt, face, **kwargs):
        # expression -> FACIAL_EXPRESSION_HAPPY("happy")
        event_name = "FaceObserved"
        self.node_instance.logger.debug(face.name)
        self.node_instance.logger.debug(face.known_expression)
        event_param = face.known_expression
        self.node_instance.logger.debug(
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
        self.node_instance.logger.debug("PetAppeared")
        self.node_instance.logger.debug(pet.pet_type)
        event_name = "PetAppeared"
        event_param = pet.pet_type
        self.pub_event(event_name, event_param)

    def onPetObserved(self, evt, pet, **kwargs):
        self.node_instance.logger.debug("PetObserved")
        self.node_instance.logger.debug(pet.pet_type)
        event_name = "PetObserved"
        event_param = pet.pet_type
        self.pub_event(event_name, event_param)

    def onPetDisappeared(self, evt, pet, **kwargs):
        self.node_instance.logger.debug("PetDisappeared")
        self.node_instance.logger.debug(pet.pet_type)
        event_name = "PetDisappeared"
        event_param = pet.pet_type
        self.pub_event(event_name, event_param)

    def onRobotObservedMotion(self, evt, **kwargs):
        event_name = "RobotObservedMotion"  # EvtRobotObservedMotion
        self.node_instance.logger.debug(event_name)
        self.pub_event(event_name)

    def cozmo_program(self, robot):
        '''
        event
            cozmo.faces.EvtFaceAppeared
            cozmo.camera.EvtRobotObservedMotion
            cozmo.world.EvtNewCameraImage
        '''
        # Object
        self.thing = robot
        self.node_instance.pub_notification("Cozmo 已连接", type="SUCCESS")
        robot.say_text("hi").wait_for_completed()
        # robot.enable_facial_expression_estimation(enable=True)
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

        # face todo 启动人脸识别 enable
        '''
        表情 启动 
            http://cozmosdk.anki.com/docs/generated/cozmo.robot.html#cozmo.robot.Robot.enable_facial_expression_estimation
            robot.enable_facial_expression_estimation(enable=True)
            http://cozmosdk.anki.com/docs/generated/cozmo.faces.html#cozmo.faces.FACIAL_EXPRESSION_UNKNOWN
        '''
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

        while self.node_instance._running:
            if self.disconnect_flag:
                # self.thing = None
                # self.is_connected = False
                break
            time.sleep(0.1)
            #  消息取来在内部运行
            '''
            if not self.node_instance.q.empty():
                payload = self.node_instance.q.get()
                # self.node_instance.logger.info(f'python: {payload}')
                python_code = payload["content"]
                try:
                    output = eval(python_code, {"__builtins__": None}, {
                        "robot": robot,
                        "cozmo": cozmo,
                    })
                except Exception as e:
                    output = e
                    self.node_instance.pub_notification(str(e), type="ERROR")
                payload["content"] = str(output)
                message = {"payload": payload}
                self.publish(message)
                # 把 message id 丢出去
            '''


class CozmoNode(AdapterNode):
    NODE_ID = "eim/node_cozmo"
    WEIGHT = 100
    HELP_URL = "https://adapter.codelab.club/extension_guide/cozmo/"
    VERSION = "2.1.0"  # 支持表情
    DESCRIPTION = "最好的 AI 教育机器人之一"

    def __init__(self, **kwargs):
        super().__init__(logger=logger, **kwargs)
        # self.q = queue.Queue()
        self.thing = CozmoProxy(self)

    def extension_message_handle(self, topic, payload):
        python_code = payload["content"]
        # if python_code.startswith("robot."):
        #     self.q.put(payload)
        try:
            output = eval(
                python_code,
                {"__builtins__": None},
                {
                    # "robot": robot,
                    "list": self.thing.list,
                    "connect": self.thing.connect,
                    "disconnect": self.thing.disconnect,
                    "robot": self.thing.thing,
                    "cozmo": cozmo,
                    "degrees": degrees,
                    "distance_mm": distance_mm,
                    "speed_mmps": speed_mmps,
                    "Pose": Pose,
                    "dir": dir,
                    "help": help
                })
        except Exception as e:
            output = e
            self.pub_notification(str(e), type="ERROR")
        try:
            output = json.dumps(output)  # 单引号 json
        except Exception:
            output = str(output)
        payload["content"] = str(output)
        message = {"payload": payload}
        self.publish(message)

    def run(self):
        while self._running:
            # "robot": self.thing.thing,
            if self.thing.thing and not self.thing.thing.world.conn.is_connected:
                self.logger.debug(f"conn: {self.thing.thing.world.conn.is_connected}")
                # self.thing.disconnect()
                self.terminate()
                self.logger.debug("go on...")
            time.sleep(0.5)
        # 发现，已经连接了，如果无法发现则说明有问题
        # 利用 except 知道不存在 list

    def terminate(self, **kwargs):
        super().terminate(**kwargs)


def main(**kwargs):
    try:
        node = CozmoNode(**kwargs)
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        node.terminate()  # Clean up before exiting
    except Exception as e:
        node.logger.error(str(e))
        node.pub_notification(str(e), type="ERROR")
        time.sleep(0.05)
        node.terminate()  # Clean up before exiting.


if __name__ == "__main__":
    main()