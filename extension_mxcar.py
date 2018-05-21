import serial
import time
import json
import threading
import multiprocessing as mp
from guizero import error

from scratch3_adapter.utils import find_microbit
from scratch3_adapter.core_extension import Extension

print("microbit ok")


def check_env():
    return find_microbit()
    # 环境是否满足要求


class MicrobitCarProxy(Extension):
    '''
        继承 Extension 之后你将获得:
            self.actuator_sub
            self.sensor_pub
            self.logger
    '''

    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)
        self.message = {}

    def run(self):
        while True:
            env_is_valid = check_env()
            # 等待用户连接microbit
            if not env_is_valid:
                try:
                    # 使其在cli下能用
                    error("错误信息", "请插入microbit")
                except RuntimeError:
                    self.logger.info("错误信息: %s", "请插入microbit")
                time.sleep(5)
            else:
                port = find_microbit()
                self.ser = serial.Serial(port, 115200, timeout=1)
                break

        # lock = threading.Lock()

        # def request():
        #     while True:
        #         self.logger.info("in process")
        #         lock.acquire()
        #         self.message = self.read()
        #         lock.release()

        # bg_task = threading.Thread(target=request)
        # self.logger.info("thread start")
        # bg_task.daemon = True
        # bg_task.start()

        while True:
            '''
            订阅到的是什么消息 消息体是怎样的
            '''
            self.message = self.read()
            message = self.message
            self.logger.info(f"message {message}")
            self.message = {}
            if message != {}:
                message = json.dumps(message) + "\r\n"
                message_bytes = message.encode('utf-8')
                self.logger.debug(message_bytes)
                self.ser.write(message_bytes)
                time.sleep(0.2)


export = MicrobitCarProxy  # 最后声明
