'''
Vector: 
    https://developer.anki.com/vector/docs/getstarted.html
    https://github.com/anki/vector-python-sdk/blob/master/examples/tutorials/02_drive_square.py
todo:
  整合到adapter中 整个打包
'''
import time
import threading
# https://github.com/pavlov99/json-rpc
# from jsonrpc import JSONRPCResponseManager, dispatcher
#  参考: https://github.com/Scratch3Lab/scratch3_adapter_extensions/blob/master/src/cozmo_server.py
from scratch3_adapter import settings
from scratch3_adapter.core_extension import Extension

import sys
# 都使用 pip3 install opencv-python --user
sys.path.append("/Users/wuwenjie/Library/Python/3.6/lib/python/site-packages")
import anki_vector
from anki_vector.util import degrees, distance_mm, speed_mmps


# 使用一个代理 proxy
class VectorProxy:
    def __init__(self, data, robot):
        self.method = data.get("method")
        self.params = data.get("params")
        self.robot = robot
        self.result = {}

    def run(self):
        '''    
        payload = {
            "method": "echo",
            "params": {"a":1,"b":2},
            # "jsonrpc": "2.0",
            # "id": 0,
        }
        '''
        robot_match = {
            # "vector/sensor": self.handle_sensor,
            "vector/say": self.say_text,
            "vector/play": self.play_anim,
            "vector/drive_straight": self.drive_straight,
            "vector/turn": self.turn,
        }
        # go on
        handle = robot_match.get(self.method, None)
        if handle:
            handle()
            self.result["state"] = "success"
        else:
            self.result["state"] = self.no_match_handle()
        return self.result

    def say_text(self):
        # ? 按位置会不会更简单
        self.robot.say_text(self.params.get("content"))

    def play_anim(self):
        # data : anim_name
        self.robot.play_anim(name=self.params.get("name"))

    def drive_straight(self):
        # Drive forwards for 150 millimeters at 50 millimeters-per-second.
        distance = int(self.params.get("distance_mm", 50))
        speed = int(self.params.get("speed_mmps", 25))
        self.robot.behavior.drive_straight(
            distance_mm(distance), speed_mmps(speed))

    def turn(self):
        # Turn 90 degrees to the left.
        # Note: To turn to the right, just use a negative number.
        angle = int(self.params.get("angle", 90))
        speed = int(self.params.get("speed", 45))
        self.robot.behavior.turn_in_place(degrees(angle), speed=degrees(speed))

    def handle_sensor(self):
        result = {}
        result["accelerometer"] = [
            self.robot.accelerometer.x, self.robot.accelerometer.y,
            self.robot.accelerometer.z
        ]
        return result

    def no_match_handle(self):
        # 404
        return "404 on match"


class VectorExtension(Extension):
    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)

    def run(self):
        # 先启动vector

        with anki_vector.Robot() as robot:
            while self._running:
                message = self.read()  # json
                self.logger.info("message:%s", str(message))
                topic = message.get("topic")
                data = message.get("data")
                if data.get("method"):
                    vector_proxy = VectorProxy(data, robot)
                    result = vector_proxy.run()
                    self.logger.info(result)


export = VectorExtension