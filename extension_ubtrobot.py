import serial
import glob
import time
import json
import threading
import platform
from scratch3_adapter.utils import ui_error

from serial.tools.list_ports import comports as list_serial_ports

from scratch3_adapter.core_extension import Extension


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
                # 旧的port会被系统留着
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
    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)

    def run(self):
        while self._running:
            '''
            连接硬件 串口
            '''
            env_is_valid = check_env()
            # 等待用户连接microbit
            if not env_is_valid:
                self.logger.info("错误信息: %s", "请插入ubtrobot")
                ui_error("错误信息", "请连接ubtrobot")
                time.sleep(5)
            else:
                try:
                    port = find_ubtrobot()
                    self.ser = serial.Serial(port, 115200, timeout=1)  # 9600
                    break
                except OSError:
                    self.logger.info("错误信息: %s", "请插入ubtrobot")
                    ui_error("错误信息", "请连接ubtrobot")
                    time.sleep(5)

        while self._running:
            '''
            订阅到的是什么消息 消息体是怎样的
            '''
            message = self.read()
            cmd_map = {
                "forward":
                [0xFB, 0xBF, 0x09, 0x03, 0xc7, 0xb0, 0xbd, 0xf8, 0x38, 0xED],
                "backward":
                [0xFB, 0xBF, 0x09, 0x03, 0xba, 0xf3, 0xcd, 0xcb, 0x51, 0xED],
                "left":
                [0xFB, 0xBF, 0x09, 0x03, 0xd7, 0xf3, 0xd7, 0xaa, 0x57, 0xED],
                "right": [
                    0xFB, 0xBF, 0x09, 0x03, 0xd3, 0xd2, 0xd7, 0xaa, 0x32, 0xED
                ],
                "push ups": [
                    0xFB, 0xBF, 0x0b, 0x03, 0xb8, 0xa9, 0xce, 0xd4, 0xb3, 0xc5,
                    0x89, 0xED
                ],
                "stop": [0xFB, 0xBF, 0x06, 0x05, 0x00, 0x0b, 0xED],
                "init": [
                    0xFB, 0xBF, 0x0b, 0x03, 0xb3, 0xf5, 0xca, 0xbc, 0xbb, 0xaf,
                    0xa6, 0xED
                ],
                "happy birthday": [
                    0xFB, 0xBF, 0x13, 0x03, 0x48, 0x61, 0x70, 0x70, 0x79, 0x20,
                    0x42, 0x69, 0x72, 0x74, 0x68, 0x64, 0x61, 0x79, 0x6f, 0xED
                ],
                "left punch": [
                    0xFB, 0xBF, 0x0b, 0x03, 0xd7, 0xf3, 0xb3, 0xf6, 0xc8, 0xad,
                    0xf6, 0xED
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


export = UbtrobotProxy
