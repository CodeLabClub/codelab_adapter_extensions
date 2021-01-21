import asyncio
import json
import time
from bleak import BleakScanner, BleakClient, BleakError
from codelab_adapter_client import AdapterNodeAio
from codelab_adapter_client.thing import AdapterThing
from codelab_adapter_client.utils import is_win

from codelab_adapter_client.config import settings
from loguru import logger
debug_log = str(settings.NODE_LOG_PATH / "adapterMario.log")
logger.add(debug_log, rotation="1 MB", level="DEBUG")


# Class for the controller
class MarioController(AdapterThing):
    LEGO_CHARACTERISTIC_UUID = "00001624-1212-efde-1623-785feabcd123"
    SUBSCRIBE_IMU_COMMAND = bytearray(
        [0x0A, 0x00, 0x41, 0x00, 0x00, 0x05, 0x00, 0x00, 0x00, 0x01])
    SUBSCRIBE_RGB_COMMAND = bytearray(
        [0x0A, 0x00, 0x41, 0x01, 0x00, 0x05, 0x00, 0x00, 0x00, 0x01])

    def __init__(self, node_instance):
        super().__init__(thing_name="Mario", node_instance=node_instance)
        self.current_x = 0
        self.current_y = 0
        self.current_z = 0
        self.is_connected = False
        self.task = None
        # self.q = queue.Queue()

    async def list(self, timeout=5) -> list:
        logger.debug("list devices...")
        try:
            devices = await BleakScanner.discover()  # todo except
        except BleakError as e:
            # 提醒开启蓝牙
            await self.node_instance.pub_notification(str(e), type="ERROR")
            return []
        logger.debug(f'devices: {devices}')
        # 单独处理windows，bleak系统兼容不好
        if is_win():
            # 条件很弱，可能会误判
            return [str(d.address) for d in devices if "lego" in str(d).lower()]
        else:
            return [
                str(d.address) for d in devices
                if d.name.lower().startswith("lego mario")
            ]

    async def _send_connect_reply(self):
        #  from RVR
        payload = self.node_instance.connect_payload
        message = {"payload": payload}
        await self.node_instance.publish(message)

    async def _connect(self, address):
        async with BleakClient(address) as client:
            await client.is_connected()
            # 连接成功反馈
            await self._send_connect_reply()
            self.is_connected = True
            await client.start_notify(self.LEGO_CHARACTERISTIC_UUID,
                                      self.notification_handler)
            await asyncio.sleep(0.1)
            await client.write_gatt_char(self.LEGO_CHARACTERISTIC_UUID,
                                         self.SUBSCRIBE_IMU_COMMAND)
            await asyncio.sleep(0.1)
            await client.write_gatt_char(self.LEGO_CHARACTERISTIC_UUID,
                                         self.SUBSCRIBE_RGB_COMMAND)
            while await client.is_connected():
                await asyncio.sleep(0.1)

    async def connect(self, address, timeout):
        if not self.thing:
            # self.thing = BleakClient(address)
            # as task
            # 等待future， 外部停掉
            self.task = asyncio.create_task(
                self._connect(address))  # todo 真正连上后发出
            # await asyncio.sleep(3)
            return True

    async def status(self):
        pass

    async def disconnect(self):
        if self.task:
            self.task.cancel()  # 让用户知道错误信息
        self.is_connected = False
        if self.thing:
            await self.thing.disconnect()
        self.thing = None
        return True

    ###  以下是具体设备驱动

    def signed(self, char):
        return char - 256 if char > 127 else char

    async def _send_to_adapter(self, content, message_type="setProperty"):
        message = self.node_instance.message_template()
        message["payload"]["message_type"] = message_type
        message["payload"]["content"] = content
        # property_notify属性的变化
        await self.node_instance.publish(message)

    def property_notify(self, data):
        '''
        msg = {
            "topic": "things/urn:lego:mario/state",
            "messageType": "setProperty",
            "data": data
        }
        '''
        logger.debug(f'data: {data}')
        asyncio.create_task(self._send_to_adapter(data))
        # self.q.put(data)  # sync -> async
        #  send to eim
        # validate_msg = InputMsg(**msg)
        # ee.emit("things/urn:lego:mario", validate_msg)

    def notification_handler(self, sender, data):
        # Camera sensor data
        # todo eim
        if data[0] == 8:
            # RGB code
            if data[5] == 0x0:
                # print(data[4])
                if data[4] == 0xb8:
                    logger.debug("Start tile")
                    self.property_notify({"barcode": "Start"})
                if data[4] == 0xb7:
                    logger.debug("Goal tile")
                    self.property_notify({"barcode": "Goal"})
                logger.debug("Barcode: " + " ".join(hex(n) for n in data))

            # Red tile
            elif data[6] == 0x15:
                # print("Red tile")
                self.property_notify({"color": "Red"})
            # Green tile
            elif data[6] == 0x25:
                # print("Green tile")
                self.property_notify({"color": "Green"})
            elif data[6] == 0x17:
                # print("Blue tile")
                self.property_notify({"color": "Blue"})
            elif data[6] == 0x17:
                # print("Blue tile")
                self.property_notify({"color": "Blue"})
            elif data[6] == 0x13:
                # print("White tile")
                self.property_notify({"color": "White"})
            elif data[6] == 0x18:
                # # print("Yellow tile")
                self.property_notify({"color": "Yellow"})
            elif data[6] == 0x6A:
                ## print("Brown tile")
                self.property_notify({"color": "Brown"})
            # No tile
            elif data[6] == 0x1a:
                # # print("No tile")
                self.property_notify({"color": "NoColor"})

        # Accelerometer data
        elif data[0] == 7:
            self.current_x = int((self.current_x * 0.5) +
                                 (self.signed(data[4]) * 0.5))
            self.current_y = int((self.current_y * 0.5) +
                                 (self.signed(data[5]) * 0.5))
            self.current_z = int((self.current_z * 0.5) +
                                 (self.signed(data[6]) * 0.5))
            self.property_notify({
                "coordinate": {
                    "x": self.current_x,
                    "y": self.current_y,
                    "z": self.current_z
                }
            })
            '''
            # 在 scratch 中处理，利用hat积木的特性: 如无变化，只发生一次
            if self.current_z > 15:
                self.property_notify({"action": "backward"})
            elif self.current_z < -15:
                self.property_notify({"action": "forward"})
            if self.current_x > 20:
                self.property_notify({"action": "jump"})  # todo? 时间？
            '''
            # # print("X: %i | Y: %i | Z: %i" % (self.current_x, self.current_y, self.current_z))


class MyNode(AdapterNodeAio):
    NODE_ID = "eim/node_adapterMario"
    HELP_URL = "https://adapter.codelab.club/extension_guide/adapterMario/"
    DESCRIPTION = "登登登等登蹬"
    VERSION = "1.1.0"

    def __init__(self):
        super().__init__(logger=logger, bucket_token=300, bucket_fill_rate=300)
        self.thing = MarioController(self)
        self.connect_payload = None

    async def run_python_code(self, code):
        try:
            output = await eval(
                code,
                {"__builtins__": None},
                {
                    # "thing": self.thing.thing,  # 推送风格
                    "connect": self.thing.connect,
                    "disconnect": self.thing.disconnect,
                    "list": self.thing.list,
                })
        except Exception as e:
            output = e
        return output

    async def extension_message_handle(self, topic, payload):
        self.logger.info(f'code: {payload["content"]}')
        python_code = payload["content"]
        if python_code.startswith('connect('):
            # connect
            self.connect_payload = payload
        output = await self.run_python_code(python_code)
        try:
            output = json.dumps(output)
        except Exception:
            output = str(output)
        if not python_code.startswith('connect('):
            # connect 连上之后（异步）发送
            payload["content"] = output
            message = {"payload": payload}
            await self.publish(message)

    def run(self):
        while self._running:
            time.sleep(0.5)

    async def terminate(self, **kwargs):
        try:
            await self.thing.disconnect()
        except Exception:
            pass
        await super().terminate(**kwargs)


if __name__ == "__main__":
    try:
        node = MyNode()
        asyncio.run(node.receive_loop())  # CPU?
    except Exception:
        if node._running:
            asyncio.run(node.terminate())
