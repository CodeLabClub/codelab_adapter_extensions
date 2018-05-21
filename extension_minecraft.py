import serial
import time
import json
import threading
import multiprocessing as mp
from guizero import error

from scratch3_adapter.utils import find_microbit
from scratch3_adapter.core_extension import Extension
from craft import MineCraft


class MineCraftProxy(Extension):
    '''
        继承 Extension 之后你将获得:
            self.actuator_sub
            self.sensor_pub
            self.logger
    '''

    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)
        self.mc = None

    def run(self):
        while True:
            message = self.read()
            topic = message.get('topic')
            data = message.get('data')
            if topic == 'init':
                self.mc = MineCraft(data)
                self.publish({"id": 'minecraft', "topic": "sensor", "is_connected": True})
            if self.mc:
                fn = self.mc.match().get(topic)
                if fn:
                    res = fn(data)
                    if res.get('topic') == 'sensor':
                        self.publish(res)
            else:
                self.publish({"id": 'minecraft', "topic": "sensor", "is_connected": False})


export = MineCraftProxy  # 最后声明
