import time
import serial

from codelab_adapter import settings
from codelab_adapter.core_extension import Extension
from guizero import info


def doRGBLed(ser, index = 0, red = 0, green = 0, blue = 0):
	ser.write(bytearray([0xff,0x55,0x9,0x0,0x2,0x8,0x7,0x2,index,red,green,blue]))  

class Test2Extension(Extension):
    def __init__(self):
        name = type(self).__name__ # class name
        super().__init__(name)
        # self.ser = serial.Serial("COM3", 115200, timeout=1)
    def run(self):
        # run 会被作为线程调用
        while self._running:
            message = self.read()
            self.logger.debug("message:%s",str(message))
            data = message.get("data")
            if data:
                R = int(data.get("R"))
                G = int(data.get("G"))
                B = int(data.get("B"))
                self.logger.info("RGB: {} {} {}".format(R,G,B))
                info("info","RGB: {} {} {}".format(R,G,B))
                # doRGBLed(self.ser,red=R, green=G, blue=B)

export = Test2Extension
