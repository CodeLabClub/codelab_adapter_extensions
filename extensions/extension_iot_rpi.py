import time
import logging
import asyncio
from queue import Queue
from threading import Event
import sys
import gpiozero # 只有rpi平台才有

from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_0

from codelab_adapter import settings
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import get_client_id, AsyncTaskManager


class RpiCar:
    def __init__(self, logger, name="myRpiCar"):
        self.name = name
        self.logger = logger

    def move_forward(self, distance):
        # todo 采用gpiozero去驱动舵机实现
        self.logger.info("move_forward:{}".format(distance))

    def move_backward(self, distance):
        self.logger.info("move_backward:{}".format(distance))


class IoTRpiExtension(Extension):
    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)
        self.queue = Queue()
        username = "guest"
        password = "test"
        self.mqtt_url = "mqtt://{}:{}@iot.codelab.club".format(
            username, password)
        self.picar = RpiCar(self.logger)

    def handle_message(self, topic, payload):
        self.logger.info("handle_message: {} {}".format(topic, payload))
        python_code = payload
        self.logger.info("run python code:{}".format(python_code))
        try:
            # 单一入口，传递源码
            # 为了安全性, 做一些能力的牺牲, 放弃使用exec
            output = eval(python_code, {"__builtins__": None}, {
                "picar": self.picar,
                "gpiozero": gpiozero
            })
            # exec(python_code) # 安全性问题
        except Exception as e:
            output = e
        self.logger.info(str(output))


    async def message_from_scratch3(self):
        '''
        接收scratch3发出的消息,消息频道为 scratch3_pub
        '''
        client_id = "adapter_iot_sub_" + get_client_id()
        C = MQTTClient(client_id=client_id)
        await C.connect(self.mqtt_url)
        scratch3_pub = '/rpi/picar'  # 消息体内做更细的分割
        await C.subscribe([
            (scratch3_pub, QOS_0),
        ])
        try:
            while self._running:
                message = await C.deliver_message()  # 阻塞
                topic = message.topic
                payload = message.data.decode()
                self.logger.info("mqtt: %s => %s" % (topic, payload))
                self.handle_message(topic, payload)
                # todo 业务代码写在合理 诸如使用消息驱动机器人
            await C.unsubscribe([scratch3_pub])
            await C.disconnect()
        except ClientException as ce:
            logging.error("Client exception: %s" % ce)

    def run(self):
        event1 = Event()
        b1 = AsyncTaskManager(event1)
        b1.setDaemon(True)
        b1.start()
        event1.wait()

        t1 = b1.add_task(self.message_from_scratch3())

        while self._running:
            time.sleep(1)

        b1.cancel_task(t1)

        time.sleep(0.5)
        b1.close()

        self.logger.info("extension iot stop thread!")
        # Q: 第二次启停 退出会报错 hbmqtt: Event loop is closed


export = IoTRpiExtension
