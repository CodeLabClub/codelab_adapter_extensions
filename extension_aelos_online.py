import time
from codelab_adapter.core_extension import Extension
import logging
import math
import serial
import serial.tools.list_ports

logger = logging.getLogger(__name__)


def arm_pose(line):
    max_limit = 175
    min_limit = 15
    # line = line.replace('\n', '')
    coors = line.split(',')
    coors = list(map(lambda x: float(x), coors))
    x_ls, y_ls, x_le, y_le, x_lw, y_lw = coors[0], coors[1], coors[2], coors[3], coors[4], coors[5]
    x_rs, y_rs, x_re, y_re, x_rw, y_rw = coors[6], coors[7], coors[8], coors[9], coors[10], coors[11]
    lse = math.sqrt((x_ls - x_le)**2 + (y_ls - y_le)**2)
    lew = math.sqrt((x_le - x_lw)**2 + (y_le - y_lw)**2)
    lsw = math.sqrt((x_ls - x_lw)**2 + (y_ls - y_lw)**2)
    rse = math.sqrt((x_rs - x_re)**2 + (y_rs - y_re)**2)
    rew = math.sqrt((x_re - x_rw)**2 + (y_re - y_rw)**2)
    rsw = math.sqrt((x_rs - x_rw)**2 + (y_rs - y_rw)**2)
    # left hand
    l_shoulder = math.asin(abs(x_le - x_ls) / lse) / math.pi * 180
    l_shoulder = l_shoulder if y_le < y_ls else 180 - l_shoulder
    l_elbow = math.acos((lse**2 + lew**2 - lsw**2) /
                        (2*lse*lew)) / math.pi * 180
    l_elbow = l_elbow - 90
    if y_lw > y_le:
        l_elbow = 180 - l_elbow
        l_elbow = l_elbow if l_elbow < max_limit else max_limit
    else:
        l_elbow = l_elbow if l_elbow > min_limit else min_limit
    # right hand
    r_shoulder = math.asin(abs(x_re - x_rs) / rse) / math.pi * 180
    r_shoulder = r_shoulder if y_re < y_rs else 180 - r_shoulder
    r_elbow = math.acos((rse**2 + rew**2 - rsw**2) /
                        (2*rse*rew)) / math.pi * 180
    r_elbow = r_elbow - 90
    if y_rw > y_re:
        r_elbow = 180 - r_elbow
        r_elbow = r_elbow if r_elbow < max_limit else max_limit
    else:
        r_elbow = r_elbow if r_elbow > min_limit else min_limit

    r_shoulder = 190 - r_shoulder
    r_elbow = 190 - r_elbow
    return int(l_shoulder), int(l_elbow), int(r_shoulder), int(r_elbow)



def auto_detect_port():
    device_desc = 'STM32 Virtual COM Port'
    vid_pid = '0483:5740'
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print("port {}: desc {} hwid {}".format(port, desc, hwid))
        if device_desc in desc and vid_pid in hwid:
            return port
    assert False, 'Aelos usb device not found!'


class WiredUsb:
    def __init__(self, port=None):
        self.port = port
        self.dongle = self.open_port(self.port)

    def open_port(self, port):
        if port is None:
            port = auto_detect_port()
        return serial.Serial(port, 9600)

    def send(self, data):
        self.dongle.write(bytes(data))

    def read(self):
        self.dongle.read_all()

    def set_channel(self, channel):
        self.send([0x29, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, channel])

    def online_mode(self):
        self.send([0xcc])
        time.sleep(0.5)
        self.send([0x83])

    def set_angles(self, data):
        assert len(data) == 16
        prefix = [0x91, 0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00]
        self.send(prefix + data)

    def set_arms(self, l_shoulder, l_elbow, r_shoulder, r_elbow):
        pose = [80, 30, 100, 100, 93, 55, 124, 100,
                120, 170, 100, 100, 107, 145, 76, 100]
        pose[0] = l_elbow
        pose[1] = l_shoulder
        pose[8] = r_elbow
        pose[9] = r_shoulder
        self.set_angles(pose)


wire = WiredUsb()
wire.online_mode()
wire.set_arms(100, 100, 100, 100)


class AelosOnline(Extension):
    def __init__(self):
        name = type(self).__name__
        super().__init__(name)

    def run(self):
        while True:
            message = self.read()
            if message["topic"] == "eim":
                payload = message['payload']
                logger.info(payload)
                l_shoulder, l_elbow, r_shoulder, r_elbow = arm_pose(payload)
                logger.info(l_shoulder)
                logger.info(l_elbow)
                logger.info(r_shoulder)
                logger.info(r_elbow)
                # wire.set_arms(100, l_elbow, 100, r_elbow)
                wire.set_arms(l_shoulder, l_elbow, r_shoulder, r_elbow)


export = AelosOnline
