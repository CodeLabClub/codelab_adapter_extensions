import time
import serial
from codelab_adapter.core_extension import Extension


def is_positive_valid(s):
    try:
        num = int(s)
        if 0 < num < 255:
            return True
        else:
            return False
    except ValueError:
        return False


def parse_cmd(content):
    cmd = 0
    if is_positive_valid(content):
        cmd = int(content)
    return cmd


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
        time.sleep(0.2)
        self.send([0x29, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, channel])


def parse_content(content):
    try:
        if type(content) == str:
            arr = content.split(':')
            if len(arr) != 2:
                return None
            return arr
    except Exception as err:
        return None


class LejuAelosEduExtention(Extension):
    """
    Leju Robotics Aelos Edu Extension V2
    """
    def __init__(self):
        super().__init__()
        self.EXTENSION_ID = "eim/leju/aelosedu"
        self.usb_dongle = Dongle2401()

    def extension_message_handle(self, topic, payload):
        self.logger.info(f'topic = {topic}')
        if type(payload) == str:
            self.logger.info(f'scratch eim message:{payload}')
            return
        elif type(payload) == dict:
            self.logger.info(f'eim message:{payload}')
            arr = parse_content(payload.get('content'))

            if arr is None:
                return

            if arr[0] == 'channel':
                ch_num = parse_cmd(arr[1])
                self.usb_dongle.set_channel(ch_num)

            if arr[0] == 'action':
                act_num = parse_cmd(arr[1])
                self.usb_dongle.send([act_num])

    def run(self):
        while self._running:
            time.sleep(1)


export = LejuAelosEduExtention

if __name__ == "__main__":
    LejuAelosEduExtention().run()  # or start_as_thread()
