'''
cozmo server : zmq rep

usage:
    python cozmo_server.py

ref:
    https://github.com/anki/cozmo-python-sdk/blob/master/examples/apps/remote_control_cozmo.py#L335
'''
import time
# time.sleep(7) # 树莓派开机等待
import zmq
# from zmq.asyncio import Context
from zmq import Context

import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps

port = 38777
context = Context.instance()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:%s" % port)

class CozmoProxy:
    def __init__(self, topic, data, robot):
        self.topic = topic
        self.data = data
        self.robot = robot

        self.result = {}
        self.result["topic"] = topic

    def run(self):
        robot_match = {
            "cozmo/sensor": self.handle_sensor,
            "cozmo/say": self.say_text,
            "cozmo/play": self.play_anim,
            "cozmo/move": self.move,
            "cozmo/turn": self.turn,
            "cozmo/pick": self.pick,
            "cozmo/move_north": self.move_north,
        }
        handle = robot_match.get(self.topic, None)
        if handle:
            handle()
            self.result["state"] = "success"
        else:
            self.result["state"] = self.no_match_handle()
        return self.result

    def say_text(self):
        self.robot.say_text(self.data).wait_for_completed()

    def play_anim(self):
        # data : anim_name
        self.robot.play_anim(name=self.data).wait_for_completed()

    def move(self):
        # Drive forwards for 150 millimeters at 50 millimeters-per-second.
        distance = self.data.get("distance",50)
        speed = self.data.get("speed",25)
        self.robot.drive_straight(distance_mm(distance),speed_mmps(speed)).wait_for_completed()

    def move_north(self):
        # Drive forwards for 150 millimeters at 50 millimeters-per-second.
        # distance = self.data.get("distance",50)
        # speed = self.data.get("speed",25)
        angle = -90
        speed = 180
        self.robot.turn_in_place(degrees(angle),speed=degrees(speed)).wait_for_completed()

        distance = 130
        speed = 200
        self.robot.drive_straight(distance_mm(distance),speed_mmps(speed)).wait_for_completed()

        angle = 90
        speed = 180
        self.robot.turn_in_place(degrees(angle),speed=degrees(speed)).wait_for_completed()

    # 移动手 left  pick

    def pick(self):
        # 挥动手臂  采摘松果 种树
        # import IPython;IPython.embed()
        self.robot.move_lift(5)
        time.sleep(0.5)
        self.robot.move_lift(-5)

    def turn(self):
        # Turn 90 degrees to the left.
        # Note: To turn to the right, just use a negative number.
        angle = self.data.get("angle",90)
        speed = self.data.get("speed",45)
        self.robot.turn_in_place(degrees(angle),speed=degrees(speed)).wait_for_completed()

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


def cozmo_program(robot: cozmo.robot.Robot):
    # import IPython;IPython.embed()
    while True:
        # 如果cozmo连接成功之后 终端，则这个while出不去，需要一个信号传递过来，或者进程被重启
        message = socket.recv_json()  # python dict
        print("cozmo server Received request: {message}".format(message=message))
        if message:
            topic, data = (message["topic"], message["data"])
            cozmo_proxy = CozmoProxy(topic, data, robot)
            result = cozmo_proxy.run()
            socket.send_json(result)

if __name__ == '__main__':
  while True:
    try:
        cozmo.run_program(cozmo_program)
        # 如果cozmo没连上则会重试
        time.sleep(60*5)
    except:
        print("wait for mobile(usb)")
        time.sleep(3)



