import asyncio
import os
import time
import json
# from hbmqtt.client import MQTTClient, ClientException
# from hbmqtt.mqtt.constants import QOS_1, QOS_2

from codelab_adapter.core_extension import Extension
import paho.mqtt.client as mqtt


class MqttAdapterExtension(Extension):
    '''
    MqttAdapter的职责: 转发进出的消息: scratch <--> mqtt

    hbmqtt_pub --url mqtt://127.0.0.1 -t to_scratch -m "mqtt message" # eim message
    hbmqtt_sub --url mqtt://127.0.0.1 -t from_scratch

    todo:
        与 broker 合并？
    '''
    def __init__(self):
        super().__init__()
        self.NODE_ID = "eim"

        # mqtt settings
        self.mqtt_addr = "127.0.0.1"
        self.mqtt_port = 1883

        self.mqtt_sub_topics = ["to_scratch"]
        # mqtt client
        self.client = mqtt.Client()
        self.client.on_connect = self.mqtt_on_connect
        self.client.on_message = self.mqtt_on_message
        # self.client.username_pw_set(self.username, self.password)
        self.client.connect(self.mqtt_addr, self.mqtt_port, 60)
        self.client.loop_start()  # as thread

    def exit_message_handle(self, topic, payload):
        # stop mqtt client
        self.client.loop_stop()
        self.terminate()

    def extension_message_handle(self, topic, payload):
        '''
        scratch eim -> mqtt
        '''
        self.logger.info(f'eim message:{payload}')
        # 来自Scratch
        # self.publish({"payload": payload})
        self.logger.info(topic, payload)
        content = payload["content"]
        # payload = json.dumps(payload).encode()
        self.client.publish("from_scratch", content.encode())

        # reply to scratch block
        payload["content"] = "ok"
        self.publish({"payload":payload})

    def mqtt_on_message(self, client, userdata, msg):
        '''
        mqtt -> scratch eim
        '''
        # topic = msg.topic  # str
        message = self.message_template()
        content  = msg.payload.decode()
        message["payload"]["content"] = content
        self.logger.debug(f"mqtt payload-> {msg.payload}")
        self.publish(message)

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


export = MqttAdapterExtension