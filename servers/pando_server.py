import zmq
from zmq import Context
import time
import queue
import uuid
import threading
import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART

# Adafruit Python BluefruitLE
# https://github.com/adafruit/Adafruit_Python_BluefruitLE.git
# TODO: support for Windows platform

port = 38789
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:%s" % port)
quit_code = "quit!"

ble = Adafruit_BluefruitLE.get_provider()
ble_cmd_queue = queue.Queue(maxsize=10)

UART_SERVICE_UUID = uuid.UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')
TX_CHAR_UUID = uuid.UUID('6E400002-B5A3-F393-E0A9-E50E24DCCA9E')
RX_CHAR_UUID = uuid.UUID('6E400003-B5A3-F393-E0A9-E50E24DCCA9E')

move_map = {
    "forward": [0xd1],
    "backward": [0xd2],
    "left": [0xd3],
    "right": [0xd4],
    "stop": [0xda]
}


def ble_thread():
    ble.clear_cached_data()
    adapter = ble.get_default_adapter()
    adapter.power_on()
    print('Using adapter: {0}'.format(adapter.name))

    print('Disconnecting any connected UART devices...')
    ble.disconnect_devices([UART_SERVICE_UUID])

    # Scan for UART devices.
    print('Searching for UART device...')
    try:
        adapter.start_scan()
        device = ble.find_device(service_uuids=[UART_SERVICE_UUID])
        print(device)
        if device is None:
            raise RuntimeError('Failed to find UART device!')
    finally:
        # Make sure scanning is stopped before exiting.
        adapter.stop_scan()

    print('Connecting to device...')
    device.connect()

    try:
        print('Discovering services...')
        device.discover([UART_SERVICE_UUID], [TX_CHAR_UUID, RX_CHAR_UUID])
        uart = device.find_service(UART_SERVICE_UUID)
        # rx = uart.find_characteristic(RX_CHAR_UUID)
        tx = uart.find_characteristic(TX_CHAR_UUID)

        while True:
            time.sleep(0.1)
            if not ble_cmd_queue.empty():
                cmd = ble_cmd_queue.get()
                tx.write_value(bytes(cmd))
    except Exception as err:
        print(err)
    finally:
        device.disconnect()


def ble_send(cmd_list):
    ble_cmd_queue.put(cmd_list, block=True)


def ble_run():
    while True:
        time.sleep(1)

    ble.initialize()
    ble.run_mainloop_with(ble_thread)


def run_in_backend(func):
    task = threading.Thread(target=func)
    task.start()


def server_loop():
    while True:
        action = socket.recv_json().get("action")
        socket.send_json({"result": "nothing"})
        print('rcv action = {}'.format(action))
        if not action:
            continue
        if action == "pando_quit":
            socket.send_json({"result": "quit!"})
            break
        cmd = move_map.get(action)
        if cmd:
            print(cmd)
            ble_send(cmd)


if __name__ == '__main__':
    # run_in_backend(server_loop)
    server_loop()
    # ble_run()
