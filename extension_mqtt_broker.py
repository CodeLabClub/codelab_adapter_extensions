'''
在本地运行一个mqtt server(MQTT message Broker)
'''
import logging
import asyncio
import os
import time
from hbmqtt.broker import Broker

from codelab_adapter import settings
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import threaded


class MqttBrokerExtension(Extension):
    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)

    async def broker_coro(self):
        # https://hbmqtt.readthedocs.io/en/latest/references/broker.html#broker-configuration
        config = {
            'listeners': {
                'default': {
                    'type': 'tcp',
                    'bind': '0.0.0.0:1883',
                    'max_connections': 50000,
                }
            },
        }
        broker = Broker(config)
        await broker.start()

    @threaded
    def task(self):

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.broker_coro())
        loop.run_forever()

    def run(self):
        self.task()

        while self._running:
            # to publish mqtt message
            time.sleep(1)


export = MqttBrokerExtension
