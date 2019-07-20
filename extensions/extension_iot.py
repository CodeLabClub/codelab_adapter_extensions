'''
IoT: Internet of Things
server : iot.codelab.club

# 保持透明

# test tool:
    pip3 install hbmqtt # 0.9.5
    hbmqtt_pub --url mqtt://guest:test@iot.codelab.club -t "/scratch3_sub" -m "hello from hbmqtt_pub"
    hbmqtt_sub --url mqtt://guest:test@iot.codelab.club -t "/scratch3_pub"
'''
import time
import logging
import asyncio
from queue import Queue
from threading import Event

from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_0

from codelab_adapter import settings
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import get_client_id, AsyncTaskManager


class IoTExtension(Extension):
    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)
        self.queue = Queue()
        username = "guest"
        password = "test"
        self.mqtt_url = "mqtt://{}:{}@iot.codelab.club".format(
            username, password)

    async def message_from_scratch3(self):
        '''
        接收scratch3发出的消息,消息频道为 scratch3_pub
        '''
        client_id = "adapter_iot_sub_" + get_client_id()
        C = MQTTClient(client_id=client_id)
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
        # C = await self.connect_to_mqtt_server()
        client_id = "adapter_iot_pub" + get_client_id()
        C = MQTTClient(client_id=client_id)
        await C.connect(self.mqtt_url)
        scratch3_sub = '/scratch3_sub'

        try:
            while self._running:
                    # if not self.queue.empty():
                    message = self.queue.get()
                    self.logger.info("mqtt_pub:{}".format(message))
                    #  todo: 在此将消息发往Scratch3
                    await C.publish(
                        '/scratch3_sub', message.encode(), qos=0x00)  # qos 0
            await C.disconnect()
        except ClientException as ce:
            self.logger.error("Client exception: %s" % ce)

    def run(self):
        event1 = Event()
        b1 = AsyncTaskManager(event1)
        b1.setDaemon(True) 
        b1.start()
        event1.wait()

        event2 = Event()
        b2 = AsyncTaskManager(event2)
        b2.setDaemon(True) 
        b2.start()
        event2.wait()

        t1 = b1.add_task(self.message_from_scratch3())
        t2 = b2.add_task(self.message_to_scratch3())

        '''
        # for test
        for i in range(3):
            self.queue.put("message:{}".format(i))
            time.sleep(1)
        '''

        while self._running:
            # to publish mqtt message
            time.sleep(1)

        b1.cancel_task(t1)
        b2.cancel_task(t2)
        b1.stop()
        b2.stop()
        time.sleep(0.5)
        b1.close()
        b2.close()
        
        self.logger.info("extension iot stop thread!")
        # Q: 第二次启停 退出会报错 hbmqtt: Event loop is closed

export = IoTExtension