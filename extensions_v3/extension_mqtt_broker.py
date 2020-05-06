'''
在本地运行一个mqtt server(MQTT message Broker)

todo 处理启停问题, 参考extension_iot.py 使用task来处理。
'''

import asyncio
import os
import time
from hbmqtt.broker import Broker

from codelab_adapter import settings
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import threaded


class MqttBrokerExtension(Extension):
    def __init__(self):
        super().__init__()
        self.NODE_ID = self.generate_node_id(__file__)

    async def broker_coro(self):
        # https://hbmqtt.readthedocs.io/en/latest/references/broker.html#broker-configuration
        # https://github.com/beerfactory/hbmqtt/blob/master/scripts/broker_script.py#L29
        default_config = {
            'listeners': {
                'default': {
                    'type': 'tcp',
                    'bind': '0.0.0.0:1883',
                },
            },
            'sys_interval': 10,
            'auth': {
                'allow-anonymous':
                True,
            },
            'topic-check': {
                'enabled': False
            }
        }
        broker = Broker(default_config)
        await broker.start()
        return broker

    @threaded
    def task(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # loop.run_until_complete(self.broker_coro())
        # loop.run_forever()

        try:
            loop.run_until_complete(self.broker_coro())
            loop.run_forever()
        except KeyboardInterrupt:
            pass
            # loop.run_until_complete(broker.shutdown())
        finally:
            loop.close()

    def run(self):
        self.task()

        while self._running:
            # to publish mqtt message
            time.sleep(1)


export = MqttBrokerExtension