import time, threading, subprocess
from codelab_adapter import settings
from codelab_adapter.core_extension import Extension

import queue
import uuid
import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART

# Adafruit Python BluefruitLE
# https://github.com/adafruit/Adafruit_Python_BluefruitLE.git
# TODO: support for Windows platform

UART_SERVICE_UUID = uuid.UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')
TX_CHAR_UUID = uuid.UUID('6E400002-B5A3-F393-E0A9-E50E24DCCA9E')
RX_CHAR_UUID = uuid.UUID('6E400003-B5A3-F393-E0A9-E50E24DCCA9E')

CMD_MAP = {
    "forward": [0xd1],
    "backward": [0xd2],
    "left": [0xd3],
    "right": [0xd4],
    "stop": [0xda]
}

ble = Adafruit_BluefruitLE.get_provider()
ble_cmd_queue = queue.Queue(maxsize=10)


def run_in_background(func):
    task = threading.Thread(target=func)
    task.start()


class PandoBle:
    def __init__(self):
        ble.clear_cached_data()
        self.adapter = ble.get_default_adapter()
        self.adapter.power_on()
        ble.disconnect_devices([UART_SERVICE_UUID])
        self.device = None
        self.uart = None
        self.tx = None
        self.rx = None

    def scan(self):
        try:
            self.adapter.start_scan()
            self.device = ble.find_device(service_uuids=[UART_SERVICE_UUID])
            if self.device is None:
                raise RuntimeError('Failed to find BLE UART device!')
        finally:
            self.adapter.stop_scan()

    def connect(self):
        self.device.connect()
        self.device.discover([UART_SERVICE_UUID], [TX_CHAR_UUID, RX_CHAR_UUID])
        self.uart = self.device.find_service(UART_SERVICE_UUID)
        self.tx = self.uart.find_characteristic(TX_CHAR_UUID)

    def send(self, cmd_list):
        if cmd_list is None:
            return
        self.tx.write_value(bytes(cmd_list))

    def disconnect(self):
        self.device.disconnect()

    def run(self):
        while True:
            time.sleep(0.1)
            if not ble_cmd_queue.empty():
                cmd = ble_cmd_queue.get()
                self.tx.write_value(cmd)


class PandoExtension(Extension):
    def __init__(self):
        name = type(self).__name__
        super().__init__(name)

    def run(self):
        while True:
            cmd = None
            message = self.read()
            payload = message.get("payload")
            if cmd and 'pando_' in payload:
                cmd = CMD_MAP.get(message.get("payload"))
                self.logger.debug("cmd:{}".format(cmd))


export = PandoExtension


