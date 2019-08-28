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
import time
import pygatt
import tenacity
import binascii

class TestExtension(Extension):
    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)
        self.TOPIC = "eim"

    def run(self):
      def read_cb(handle, value):
          bytes_str = binascii.hexlify(value)
          print(bytes_str)

      dongle = Dongle()
      try:
          dongle.bled_start()

          dongle.bled_connect('D5:04:1C:07:C1:C6') # micro:bit mac-address

          dongle.bled_subscribe('5261da01-fa7e-42ab-850b-7c80220097cc', callback=read_cb)

          while True:
              time.sleep(1)
      finally:
          dongle.bled_stop()


export = TestExtension
