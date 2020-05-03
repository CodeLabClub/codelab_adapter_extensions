import binascii
import time

import pygatt
import tenacity


# pygatt api doc : https://github.com/peplin/pygatt/blob/master/pygatt/device.py
class Dongle:
    '''
    作为服务
    '''
    def __init__(self):
        self.adapter = pygatt.BGAPIBackend()
        self.device = None
        self.is_running = True

    @tenacity.retry(stop=tenacity.stop_after_attempt(3))
    def bled_start(self):
        self.adapter.start()

    def bled_stop(self):
        self.adapter.stop()
        self.is_running = False

    def bled_scan(self):
        devices = self.adapter.scan()
        return devices

    def bled_rssi(self):
        return self.device.get_rssi()

    @tenacity.retry(stop=tenacity.stop_after_attempt(3))
    def bled_connect(self, mac_addr):
        self.device = self.adapter.connect(mac_addr, address_type=pygatt.BLEAddressType.random)
        print('connect to {}'.format(mac_addr))
        print("rssi   : " + str(self.device.get_rssi()))
        print("chars  : " + str(self.device.discover_characteristics()))
        time.sleep(1)

    def bled_subscribe(self, uuid, callback=None, indication=False):
        self.device.subscribe(uuid, callback=callback, indication=indication)

    def bled_write(self, uuid, data):
        self.device.char_write(uuid, bytearray(data))

    def bled_read(self, uuid):
        data = self.device.char_read(uuid)
        return data

    @staticmethod
    def _ascii_to_hex(rawhex):
        return binascii.unhexlify(rawhex)


if __name__ == '__main__':

    def read_cb(handle, value):
        bytes_str = binascii.hexlify(value)
        print(bytes_str)

    dongle = Dongle()
    try:
        dongle.bled_start()

        devices = dongle.bled_scan()
        for dev in devices:
            print(dev.get('address'), dev.get('rssi'), dev.get('name'))
            if "micro" in dev.get('name'):
                pass
                #import IPython;IPython.embed()
                #import sys;sys.exit()

        dongle.bled_connect('C1:68:4E:87:AD:70')

        dongle.bled_subscribe('0000ffe4-0000-1000-8000-00805f9a34fb', callback=read_cb)

        data = dongle.bled_read('0000ffe4-0000-1000-8000-00805f9a34fb')
        print('data = ', data)

        while True:
            time.sleep(1)
    finally:
        dongle.bled_stop()
