'''
EIM: Everything Is Message
'''
import time
import threading

from codelab_adapter import settings
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import threaded
# from pymata_aio.pymata3 import PyMata3
from codelab_adapter.dongle import Dongle


class TestExtension(Extension):
    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)
        self.TOPIC = "eim"

    def run(self):
        dongle = Dongle()
        try:
          dongle.bled_start()
          devices = dongle.bled_scan()
          for dev in devices:
            self.logger.info("{} {} {}".format(dev.get('address'), dev.get('rssi'), dev.get('name')))
          while self._running:
            time.sleep(1)
        finally:
            dongle.bled_stop()


export = TestExtension
