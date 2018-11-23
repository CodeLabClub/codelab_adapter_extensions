import serial
import glob
import time
import json
import threading
import platform
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
    target_port = None
    if (platform.system() == "Darwin"):
        for port in ports:
            if "Alpha1_" in port[0]:
                target_port = port[0]

    if platform.system() == "Windows":
        # 分别处理win7和win10 没必要 platform.release()

        # win7会存贮之前的连接信息
        win_ports = []
        for port in ports:
            # ServiceGUID
            # 00010039_PID win7需要这个
            if ("00001101-0000-1000-8000-00805f9b34fb" in port[2].lower()
                ) and ("00010039_pid" in port[2].lower()):
                # 找到最大的(for 循环默认从小到大吗)，旧的port会被系统留着
                win_ports.append(str(port[0]))
        target_port = sorted(win_ports)[-1]  # 选择最大的

    if platform.system() == "Linux":
        target_port = find_linux_port()

    return target_port


def find_linux_port():
    # 返回数字最大的 /dev/rfcomm
    ports = glob.glob('/dev/rfcomm*')
    sorted_ports = sorted(ports)
    target = sorted_ports[-1]
    return target


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

    def run(self):
        while self._running:
            '''
            连接硬件 串口
            '''
            env_is_valid = check_env()
            if not env_is_valid:
                try:
                    # 使其在cli下能用
                    error("错误信息", "请连接ubtrobot")
                except RuntimeError:
                    self.logger.info("错误信息: %s", "请插入ubtrobot")
                time.sleep(5)
            else:
                try:
                    port = find_ubtrobot()
                    self.ser = serial.Serial(port, 115200, timeout=1)  # 9600
                    break
                except OSError:
                    try:
                        # 使其在cli下能用
                        error("错误信息", "请连接ubtrobot")
                    except RuntimeError:
                        self.logger.info("错误信息: %s", "请插入ubtrobot")
                    time.sleep(5)

        while self._running:
            '''
            订阅到的是什么消息 消息体是怎样的
            '''
            message = self.read()
            cmd_map = {
                "forward":
                [],
                "backward":
                [],
                "left":
                [],
                "right": [
                ],
                "push ups": [
                ],
                "stop": [],
                "init": [
                ],
                "happy birthday": [
                ],
                "left punch": [
                ]
            }
            self.logger.debug("message {}".format(message))
            if message.get("topic") == "eim":
                cmd = cmd_map.get(message.get("data"))
            if cmd:
                self.logger.debug("cmd:{}".format(cmd))
                # 如果是linux每次都要重连
                if platform.system() == "Linux":
                    port = find_linux_port()
                    self.ser = serial.Serial(port, 115200, timeout=1)
                self.ser.write(cmd)
            # response
            # res = get_response() # 获取串口数据
            # self.publish(res)
            # time.sleep(0.05)


export = UbtrobotProxy  # 最后声明
