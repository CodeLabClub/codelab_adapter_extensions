import serial
import subprocess
import time
from codelab_adapter.core_extension import Extension

import logging
logger = logging.getLogger(__name__)


class Dongle2401:
    def __init__(self):
        self.id = '1A86:7523'
        self.port = self.auto_detect()
        self.dongle = self.open_port(self.port)

    def auto_detect(self):
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            # print("port = {}; desc = {} ;hwid = {}".format(port, desc, hwid))
            if self.id in hwid:
                try:
                    with serial.Serial(port, 9600) as ser:
                        ser.close()
                    print('found port {}'.format(port))
                    return port
                except Exception as err:
                    pass
                    # print('open port failed', port, err)

        assert False, 'Aelos usb dongle not found!'

    def open_port(self, port):
        return serial.Serial(port, 9600)

    def send(self, data):
        self.dongle.write(bytes(data))

    def set_channel(self, channel):
        self.send([0xcc, 0xcc, 0xcc, 0xcc, 0xcc])
        time.sleep(0.5)
        self.send([0x29, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, channel])


def is_positive_valid(s):
    try:
        num = int(s)
        if 0 < num < 255:
            return True
        else:
            return False
    except ValueError:
        return False


def parse_cmd(payload):
    cmd = 0
    if is_positive_valid(payload):
        cmd = int(payload)
    return cmd


class LejuAelosRobotExtention(Extension):
    def __init__(self):
        name = type(self).__name__
        super().__init__(name)

    def run(self):
        dongle = Dongle2401()
        while True:
            message = self.read()
            if message["topic"] == "leju/aelos/action":
                action_num = parse_cmd(message.get('payload'))
                logger.info(action_num)
                dongle.send([action_num])
            if message["topic"] == "leju/aelos/channel":
                action_num = parse_cmd(message.get('payload'))
                logger.info(action_num)
                dongle.set_channel(action_num)


export = LejuAelosRobotExtention
