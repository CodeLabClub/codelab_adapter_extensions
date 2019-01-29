import time

from codelab_adapter import settings
from codelab_adapter.core_extension import Extension

import sys;sys.path.append("/usr/local/lib/python3.6/site-packages")
from pyparrot.Minidrone import Mambo


class FlyExtension(Extension):
    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)

    def run(self):
        # you will need to change this to the address of YOUR mambo
        mamboAddr = "e0:14:d0:63:3d:d0"

        # make my mambo object
        mambo = Mambo(mamboAddr, use_wifi=True)
        print("trying to connect")
        success = mambo.connect(num_retries=3)
        print("connected: %s" % success)
        print("sleeping")
        mambo.smart_sleep(2)
        mambo.ask_for_state_update()
        mambo.smart_sleep(2)
        print("taking off!")
        mambo.safe_takeoff(3)
        # from IPython import embed;embed()
        # mambo.fly_direct(roll=0, pitch=0, yaw=0, vertical_movement=50, duration=1)
        while self._running:
            message = self.read()
            self.logger.info("message:%s", str(message))
            data = message.get("data")
            if data:
                if data == "turn around":
                    mambo.turn_degrees(90)
                if data == "up":
                    # self.logger.info("up!!") # ok
                    # https://jingtaozf.gitbooks.io/crazepony-gitbook/content/wiki/pitch-yaw-roll.html
                    mambo.fly_direct(
                        roll=0,
                        pitch=0,
                        yaw=0,
                        vertical_movement=50,
                        duration=0.5)
                if data == "down":
                    # self.logger.info("down!!") # ok
                    mambo.fly_direct(
                        roll=0,
                        pitch=0,
                        yaw=0,
                        vertical_movement=-50,
                        duration=0.5)
                if data == "flip":
                    success = mambo.flip(direction="back")
        mambo.safe_land(5)


export = FlyExtension
