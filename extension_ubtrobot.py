import serial
import time
import json
import threading
# scratch3_adapter cli模式下不要使用tkinter
from guizero import error
from serial.tools.list_ports import comports as list_serial_ports

# from scratch3_adapter.utils import find_microbit # find ubtrobot
from scratch3_adapter.core_extension import Extension

# https://scratch3-adapter-docs.just4fun.site/dev_guide/helloworld/

def find_ubtrobot():
    """
    Finds the port to which the device is connected.
    https://github.com/mu-editor/mu/blob/803153f661097260206ed2b7cc9a1e71b564d7c3/mu/contrib/microfs.py#L44
    """
    ports = list_serial_ports()
    for port in ports:
        if "Alpha1_E566" in port[0]:
            return port[0]
    return None


def check_env():
    return find_ubtrobot()
    # 环境是否满足要求


class UbtrobotProxy(Extension):
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
            '''
            连接硬件 串口
            '''
            env_is_valid = check_env()
            # 等待用户连接microbit
            if not env_is_valid:
                try:
                    # 使其在cli下能用
                    error("错误信息", "请连接ubtrobot")
                except RuntimeError:
                    self.logger.info("错误信息: %s", "请插入ubtrobot")
                time.sleep(5)
            else:
                port = find_ubtrobot()
                self.ser = serial.Serial(port, 115200, timeout=1) # 9600
                break

        while True:
            '''
            订阅到的是什么消息 消息体是怎样的
            '''
            message = self.read()
            # 由于优必选alpha1的蓝牙协议没有公开，所以我暂时不把它放出来，统一用[]代替，有拿到合作的小伙伴，可以自行补上协议
            cmd_map={
                "forward":[],
                "backward":[],
                "left":[],
                "right":[],
                "push ups": [],
                "stop": [],
                "init": [],
                "happy birthday": [],
                "left punch": []
            }
            self.logger.debug("message {}".format(message))
            if message["topic"] == "eim":
                cmd = cmd_map.get(message.get("data"))
            if cmd:
                self.logger.debug("cmd:{}".format(cmd))
                self.ser.write(cmd)
            # response
            # res = get_response() # 获取串口数据
            # self.publish(res)
            # time.sleep(0.05)


export = UbtrobotProxy  # 最后声明
