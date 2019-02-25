'''
IoT: Internet of Things
server : iot.codelab.club

# tool:
    pip3 install hbmqtt # 0.9.5
    hbmqtt_pub --url mqtt://guest:test@iot.codelab.club -t "/scratch3_sub" -m "hello from hbmqtt_pub"
    hbmqtt_sub --url mqtt://guest:test@iot.codelab.club -t "/scratch3_pub"
'''
import time
import logging
import asyncio
import threading
from queue import Queue

from codelab_adapter import settings
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import threaded

from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_0


class IoTExtension(Extension):
    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)
        # self.TOPIC = "iot"
        self.mqtt_exit_flag = False
        self.queue = Queue()
        username = "guest"
        password = "test"
        self.mqtt_url = "mqtt://{}:{}@iot.codelab.club".format(
            username, password)

    async def message_from_scratch3(self):
        '''
        接收scratch3发出的消息,消息频道为 scratch3_pub
        '''
        # 保持透明
        C = MQTTClient()  # clientid?
        await C.connect(self.mqtt_url)
        scratch3_pub = '/scratch3_pub'  # 消息体内做更细的分割
        await C.subscribe([
            (scratch3_pub, QOS_0),
        ])
        try:
            while self._running:
                message = await C.deliver_message()  # 阻塞
                topic = message.topic
                payload = message.data.decode()
                self.logger.info("mqtt: %s => %s" % (topic, payload))
                # todo 业务代码写在合理 诸如使用消息驱动机器人
            await C.unsubscribe([scratch3_pub])
            await C.disconnect()
        except ClientException as ce:
            logging.error("Client exception: %s" % ce)

    async def message_to_scratch3(self):
        '''
        发送消息给scratch3正在订阅的频道scratch3_sub
        '''
        C = MQTTClient()
        await C.connect(self.mqtt_url)
        scratch3_sub = '/scratch3_sub'
        try:
            while self._running:
                message = self.queue.get()
                self.logger.info("mqtt_pub:{}".format(message))
                #  todo: 在此将消息发往Scratch3
                await C.publish('/scratch3_sub', message.encode(), qos=0x00)
            await C.disconnect()
        except ClientException as ce:
            self.logger.error("Client exception: %s" % ce)

    @threaded
    def task1(self):
        # https://stackoverflow.com/questions/46727787/runtimeerror-there-is-no-current-event-loop-in-thread-in-async-apscheduler
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.message_from_scratch3())
        # Q: 两个一起就会有问题
        '''
        loop.run_until_complete(asyncio.gather(
            self.run_mqtt_sub(),
            # self.run_mqtt_pub()
        ))
        '''

    @threaded
    def task2(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.message_to_scratch3())

    def run(self):
        self.task1()
        self.task2()

        # as demo
        #'''
        for i in range(3):
            self.queue.put("message:{}".format(i))
            time.sleep(1)
        #'''
        while self._running:
            # to publish mqtt message
            time.sleep(1)
        time.sleep(0.2)


export = IoTExtension