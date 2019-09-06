'''
to_mqtt
from_mqtt
'''

import asyncio
import os
import time
import json
# from hbmqtt.client import MQTTClient, ClientException
# from hbmqtt.mqtt.constants import QOS_1, QOS_2

from codelab_adapter.settings import FROM_MQTT_TOPIC, TO_MQTT_TOPIC, SCRATCH_TOPIC
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import threaded
import paho.mqtt.client as mqtt


class MqttGatewayExtension(Extension):
    '''
    gateway的职责: 转发进出的消息: from_mqtt/to_mqtt

    hbmqtt_pub --url mqtt://guest:test@iot.codelab.club -t 'eim/mqtt_gateway' -m "hello from hbmqtt"
    '''

    def __init__(self):
        super().__init__(external_message_processor=self.external_message_processor)
        self.EXTENSION_ID = "eim/mqtt_gateway"
        self.set_subscriber_topic(TO_MQTT_TOPIC)  # sub zmq message
        self.mqtt_sub_topics = [FROM_MQTT_TOPIC]

        # mqtt settings
        self.mqtt_addr = "iot.codelab.club"
        self.username = "guest"
        self.password = "test"
        self.mqtt_port = 1883

        # mqtt client
        self.client = mqtt.Client()
        self.client.on_connect = self.mqtt_on_connect
        self.client.on_message = self.mqtt_on_message
        self.client.username_pw_set(self.username, self.password)
        self.client.connect(self.mqtt_addr, self.mqtt_port, 60)
        self.client.loop_start()  # as thread

    def exit_message_handle(self, topic, payload):
        # stop mqtt client
        self.client.loop_stop()
        self.terminate()

    def external_message_processor(self, topic, payload):
        '''
        zmq -> mqtt
        注意 进出消息格式不同

        设计: 将Scratch的消息都转发？允许mqtt client handle
        '''
        if topic == TO_MQTT_TOPIC:
            self.logger.info(topic, payload)
            payload = json.dumps(payload).encode()
            self.client.publish(TO_MQTT_TOPIC, payload)

        if topic == SCRATCH_TOPIC:
            '''
            转发scratch消息
            '''
            zmq_message = {}
            zmq_message["zmq_topic"] = SCRATCH_TOPIC
            zmq_message["zmq_payload"] = payload
            self.client.publish(TO_MQTT_TOPIC, json.dumps(zmq_message).encode())

    def mqtt_on_message(self, client, userdata, msg):
        '''
        mqtt -> zmq
        传递json 而不是content
        '''
        topic = msg.topic  # str
        if topic == FROM_MQTT_TOPIC:
            m = msg.payload.decode()  # 在通道的两端做好decode和encode
            payload = json.loads(m)  # json
            zmq_topic = payload["zmq_topic"]
            zmq_payload = payload["zmq_payload"]
            self.logger.info(f'mqtt topic:{topic} payload: {payload}')
            self.publish_payload(zmq_payload, zmq_topic)
    
    def mqtt_on_connect(self, client, userdata, flags, rc):
        self.logger.info(
            "MQTT Gateway Connected to MQTT {}:{} with result code {}.".format(
                self.mqtt_addr, self.mqtt_port, str(rc)))
        # when mqtt is connected to subscribe to mqtt topics
        if self.mqtt_sub_topics:
            for sub in self.mqtt_sub_topics:
                self.client.subscribe(sub)

    def run(self):

        while self._running:
            # to publish mqtt message
            time.sleep(0.1)


export = MqttGatewayExtension