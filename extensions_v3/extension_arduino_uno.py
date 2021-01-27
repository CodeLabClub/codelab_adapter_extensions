import argparse
import asyncio
import logging
import pathlib
import sys
import functools

from pymata_express.private_constants import PrivateConstants
from pymata_express.pymata_express import PymataExpress

from codelab_adapter.gateway_base import GatewayBaseAIO


# noinspection PyAbstractClass,PyMethodMayBeStatic,PyRedundantParentheses,DuplicatedCode
class ArduinoGateway(GatewayBaseAIO): # 直接回复
    '''
    use TokenBucket to limit message rate(pub) https://github.com/CodeLabClub/codelab_adapter_client_python/blob/master/codelab_adapter_client/utils.py#L25
    '''
    # This class implements the GatewayBase interface adapted for asyncio.
    # It supports Arduino boards, tested with Uno.

    # NOTE: This class requires the use of Python 3.7 or above
    
    NODE_ID = "eim/extension_arduino_uno"
    HELP_URL = "http://adapter.codelab.club/extension_guide/arduino_UNO/"
    WEIGHT = 94
    DESCRIPTION = "将Arduino积木化"
    
    def __init__(self,
                 event_loop=None,
                 com_port=None,
                 arduino_instance_id=None,
                 keep_alive=False,
                 log=True,
                 bucket_token=20,
                 bucket_fill_rate=10,
                 **kwargs # 暂未处理启动提醒
                 ):

        # set the event loop to be used. accept user's if provided
        self.event_loop = event_loop
        if not self.event_loop:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.event_loop = loop

        self.log = log
        # instantiate pymata express to control the arduino
        # if user want to pass in a com port, then pass it in
        try:
            if com_port:
                self.arduino = PymataExpress(loop=self.event_loop,
                                             com_port=com_port)
            # if user wants to set an instance id, then pass it in
            elif arduino_instance_id:
                self.arduino = PymataExpress(
                    loop=self.event_loop,
                    arduino_instance_id=arduino_instance_id)
            # default settings
            else:
                self.arduino = PymataExpress(loop=self.event_loop)
        except RuntimeError as e:
            if self.log:
                logging.exception("Exception occurred", exc_info=True)
            raise
        # 正常
        self.connect_status = "connected"
        # extract pin info from self.arduino
        self.number_of_digital_pins = len(self.arduino.digital_pins)
        self.number_of_analog_pins = len(self.arduino.analog_pins)
        self.first_analog_pin = self.arduino.first_analog_pin

        # Initialize the parent
        super().__init__(bucket_token=bucket_token, bucket_fill_rate=bucket_fill_rate, **kwargs)

        self.first_analog_pin = self.arduino.first_analog_pin
        self.keep_alive = keep_alive

        # self.event_loop.create_task(pub_notification_coroutine)

    def init_pins_dictionary(self):
        """
        This method will initialize the pins dictionary contained
        in gateway base parent class. This method is called by
        the gateway base parent in its init method.

        NOTE: that this a a non-asyncio method.
        """
        report = self.event_loop.run_until_complete(
            self.arduino.get_capability_report())
        x = 0
        pin = 0
        while x < len(report):
            while report[x] != 127:
                mode = report[x]
                if mode == PrivateConstants.INPUT:
                    self.pins_dictionary[pin] = \
                        [GatewayBaseAIO.DIGITAL_INPUT_MODE, 0, False]
                elif mode == PrivateConstants.ANALOG:
                    self.pins_dictionary[pin + self.first_analog_pin] = \
                        [GatewayBaseAIO.ANALOG_INPUT_MODE, 0, False]
                x += 1
            x += 1
            pin += 1
        # set up entry for i2c as pin 200 ( a pseudo pin number)
        self.pins_dictionary[200] = GatewayBaseAIO.DIGITAL_INPUT_MODE

    async def digital_write(self, topic, payload):
        """
        This method performs a digital write
        :param topic: message topic
        :param payload content: {"command": "digital_write", "pin": “PIN”, "value": “VALUE”}
        """
        await self.arduino.digital_write(payload['content']["pin"],
                                         payload['content']['value'])

    async def disable_analog_reporting(self, topic, payload):
        """
        This method disables analog input reporting for the selected pin.
        :param topic: message topic
        :param payload content: {"command": "disable_analog_reporting", "pin": “PIN”, "tag": "TAG"}
        """
        await self.arduino.disable_analog_reporting(payload['content']["pin"])

    async def disable_digital_reporting(self, topic, payload):
        """
        This method disables digital input reporting for the selected pin.

        :param topic: message topic
        :param payload content: {"command": "disable_digital_reporting", "pin": “PIN”, "tag": "TAG"}
        """
        await self.arduino.disable_digital_reporting(payload['content']["pin"])

    async def enable_analog_reporting(self, topic, payload):
        """
        This method enables analog input reporting for the selected pin.
        :param topic: message topic
        :param payload content:  {"command": "enable_analog_reporting", "pin": “PIN”, "tag": "TAG"}
        """
        await self.arduino.enable_analog_reporting(payload['content']["pin"])

    async def enable_digital_reporting(self, topic, payload):
        """
        This method enables digital input reporting for the selected pin.
        :param topic: message topic
        :param payload content: {"command": "enable_digital_reporting", "pin": “PIN”, "tag": "TAG"}
        """
        await self.arduino.enable_digital_reporting(payload['content']["pin"])

    async def i2c_read(self, topic, payload):
        """
        This method will perform an i2c read by specifying the i2c
        device address, i2c device register and the number of bytes
        to read.

        Call set_mode_i2c first to establish the pins for i2c operation.

        :param topic: message topic
        :param payload content: {"command": "i2c_read", "pin": “PIN”, "tag": "TAG",
                         "addr": “I2C ADDRESS, "register": “I2C REGISTER”,
                         "number_of_bytes": “NUMBER OF BYTES”}
        :return via the i2c_callback method
        """

        await self.arduino.i2c_read(payload['content']['addr'],
                                    payload['content']['register'],
                                    payload['content']['number_of_bytes'],
                                    callback=self.i2c_callback)

    async def i2c_write(self, topic, payload):
        """
        This method will perform an i2c write for the i2c device with
        the specified i2c device address, i2c register and a list of byte
        to write.

        Call set_mode_i2c first to establish the pins for i2c operation.

        :param topic: message topic
        :param payload content: {"command": "i2c_write", "pin": “PIN”, "tag": "TAG",
                         "addr": “I2C ADDRESS, "register": “I2C REGISTER”,
                         "data": [“DATA IN LIST FORM”]}
        """
        await self.arduino.i2c_write(payload['content']['addr'],
                                     payload['content']['data'])

    async def play_tone(self, topic, payload):
        """
        This method plays a tone on a piezo device connected to the selected
        pin at the frequency and duration requested.
        Frequency is in hz and duration in milliseconds.

        Call set_mode_tone before using this method.
        :param topic: message topic
        :param payload content: {"command": "play_tone", "pin": “PIN”, "tag": "TAG",
                         “freq”: ”FREQUENCY”, duration: “DURATION”}
        """
        await self.arduino.play_tone(payload['content']['pin'],
                                     payload['content']['freq'],
                                     payload['content']['duration'])

    async def pwm_write(self, topic, payload):
        """
        This method sets the pwm value for the selected pin.
        Call set_mode_pwm before calling this method.
        :param topic: message topic
        :param payload content: {“command”: “pwm_write”, "pin": “PIN”,
                         "tag":”TAG”,
                          “value”: “VALUE”}
        """
        await self.arduino.analog_write(payload['content']["pin"],
                                        payload['content']['value'])

    async def servo_position(self, topic, payload):
        """
        This method will set a servo's position in degrees.
        Call set_mode_servo first to activate the pin for
        servo operation.

        :param topic: message topic
        :param payload content: {'command': 'servo_position',
                         "pin": “PIN”,'tag': 'servo',
                        “position”: “POSITION”}
        """
        await self.arduino.servo_write(payload['content']["pin"],
                                       payload['content']["position"])

    async def set_mode_analog_input(self, topic, payload):
        """
        This method sets a GPIO pin as analog input.
        :param topic: message topic
        :param payload content: {"command": "set_mode_analog_input", "pin": “PIN”, "tag":”TAG” }
        """
        pin = payload['content']["pin"]
        self.pins_dictionary[pin + self.first_analog_pin][GatewayBaseAIO.PIN_MODE] = \
            GatewayBaseAIO.ANALOG_INPUT_MODE
        await self.arduino.set_pin_mode_analog_input(
            pin, self.analog_input_callback)

    async def set_mode_digital_input(self, topic, payload):
        """
        This method sets a pin as digital input.
        :param topic: message topic
        :param payload content: {"command": "set_mode_digital_input", "pin": “PIN”, "tag":”TAG” }
        """
        pin = payload['content']["pin"]
        self.pins_dictionary[pin][
            GatewayBaseAIO.PIN_MODE] = GatewayBaseAIO.DIGITAL_INPUT_MODE
        await self.arduino.set_pin_mode_digital_input(
            pin, self.digital_input_callback)

    async def set_mode_digital_input_pullup(self, topic, payload):
        """
        This method sets a pin as digital input with pull up enabled.
        :param topic: message topic
        :param payload content: message payload
        """
        pin = payload['content']["pin"]
        self.pins_dictionary[pin][
            GatewayBaseAIO.PIN_MODE] = GatewayBaseAIO.DIGITAL_INPUT_PULLUP_MODE
        await self.arduino.set_pin_mode_digital_input_pullup(
            pin, self.digital_input_callback)

    async def set_mode_digital_output(self, topic, payload):
        """
        This method sets a pin as a digital output pin.
        :param topic: message topic
        :param payload content: {"command": "set_mode_digital_output", "pin": PIN, "tag":”TAG” }
        """
        pin = payload['content']["pin"]
        self.pins_dictionary[pin][
            GatewayBaseAIO.PIN_MODE] = GatewayBaseAIO.DIGITAL_OUTPUT_MODE
        await self.arduino.set_pin_mode_digital_output(pin)

    async def set_mode_i2c(self, topic, payload):
        """
        This method sets up the i2c pins for i2c operations.
        :param topic: message topic
        :param payload content: {"command": "set_mode_i2c"}
        """
        self.pins_dictionary[200][
            GatewayBaseAIO.PIN_MODE] = GatewayBaseAIO.I2C_MODE
        await self.arduino.set_pin_mode_i2c()

    async def set_mode_pwm(self, topic, payload):
        """
        This method sets a GPIO pin capable of PWM for PWM operation.
        :param topic: message topic
        :param payload content: {"command": "set_mode_pwm", "pin": “PIN”, "tag":”TAG” }
        """
        pin = payload['content']["pin"]
        self.pins_dictionary[pin][
            GatewayBaseAIO.PIN_MODE] = GatewayBaseAIO.PWM_OUTPUT_MODE
        await self.arduino.set_pin_mode_pwm(pin)

    async def set_mode_servo(self, topic, payload):
        """
        This method establishes a GPIO pin for servo operation.
        :param topic: message topic
        :param payload content: {"command": "set_mode_servo", "pin": “PIN”, "tag":”TAG” }
        """
        pin = payload['content']["pin"]
        self.pins_dictionary[pin][
            GatewayBaseAIO.PIN_MODE] = GatewayBaseAIO.SERVO_MODE
        await self.arduino.set_pin_mode_servo(pin)

    async def set_mode_sonar(self, topic, payload):
        """
        This method sets the trigger and echo pins for sonar operation.
        :param topic: message topic
        :param payload content: {"command": "set_mode_sonar", "trigger_pin": “PIN”, "tag":”TAG”
                         "echo_pin": “PIN”"tag":”TAG” }
        """

        trigger = payload['content']["trigger_pin"]
        echo = payload['content']["echo_pin"]
        self.pins_dictionary[trigger][
            GatewayBaseAIO.PIN_MODE] = GatewayBaseAIO.SONAR_MODE
        self.pins_dictionary[echo][
            GatewayBaseAIO.PIN_MODE] = GatewayBaseAIO.SONAR_MODE

        await self.arduino.set_pin_mode_sonar(trigger,
                                              echo,
                                              cb=self.sonar_callback)

    async def set_mode_stepper(self, topic, payload):
        """
        This method establishes either 2 or 4 GPIO pins to be used in stepper
        motor operation.
        :param topic:
        :param payload content:{"command": "set_mode_stepper", "pins": [“PINS”],
                        "steps_per_revolution": “NUMBER OF STEPS”}
        """
        for pin in payload['content']['pins']:
            self.pins_dictionary[pin][
                GatewayBaseAIO.PIN_MODE] = GatewayBaseAIO.STEPPER_MODE
        await self.arduino.set_pin_mode_stepper(
            payload['content']['steps_per_revolution'],
            payload['content']['pins'])

    async def set_mode_tone(self, topic, payload):
        """
        Establish a GPIO pin for tone operation.
        :param topic:
        :param payload content:{"command": "set_mode_tone", "pin": “PIN”, "tag":”TAG” }
        """
        pin = payload['content']["pin"]
        self.pins_dictionary[pin][
            GatewayBaseAIO.PIN_MODE] = GatewayBaseAIO.TONE_MODE
        await self.arduino.set_pin_mode_tone(pin)

    async def stepper_write(self, topic, payload):
        """
        Move a stepper motor for the specified number of steps.
        :param topic:
        :param payload content: {"command": "stepper_write", "motor_speed": “SPEED”,
                         "number_of_steps":”NUMBER OF STEPS” }
        """
        await self.arduino.stepper_write(payload['content']['motor_speed'],
                                         payload['content']['number_of_steps'])

    # Callbacks
    async def digital_input_callback(self, data):
        """
        Digital input data change reported by Arduino
        :param data:
        :return:
        """
        # data = [pin, current reported value, pin_mode, timestamp]
        self.pins_dictionary[data[0]][GatewayBaseAIO.LAST_VALUE] = data[1]

        message = self.message_template()
        message["payload"]["content"] = {
            'report': 'digital_input',
            'pin': data[0],
            'value': data[1],
            'timestamp': data[3]
        }
        await self.publish(message)

    async def analog_input_callback(self, data):
        # data = [pin, current reported value, pin_mode, timestamp]
        self.pins_dictionary[data[0] + self.arduino.first_analog_pin][
            GatewayBaseAIO.LAST_VALUE] = data[1]
        message = self.message_template()
        message["payload"]["content"] = {
            'report': 'analog_input',
            'pin': data[0],
            'value': data[1],
            'timestamp': data[3]
        }
        await self.publish(message)

    async def i2c_callback(self, data):
        """
        Analog input data change reported by Arduino

        :param data:
        :return:
        """
        # creat a string representation of the data returned
        self.pins_dictionary[200] = data[1]
        report = ', '.join([str(elem) for elem in data])
        message = self.message_template()
        message["payload"]["content"] = {'report': 'i2c_data', 'value': report}
        await self.publish(message)

    async def sonar_callback(self, data):
        """
        Sonar data change reported by Arduino

        :param data:
        :return:
        """
        self.pins_dictionary[data[0]][GatewayBaseAIO.LAST_VALUE] = data[1]
        message = self.message_template()
        message["payload"]["content"] = {
            'report': 'sonar_data',
            'value': data[1]
        }
        await self.publish(message)

    def my_handler(self, tp, value, tb):
        """
        for logging uncaught exceptions
        :param tp:
        :param value:
        :param tb:
        :return:
        """
        self.logger.exception("Uncaught exception: {0}".format(str(value)))

    async def main(self):
        # call the inherited begin method located in banyan_base_aio
        # await self.receive_loop()

        # start the keep alive on the Arduino if enabled
        if self.keep_alive:
            await self.arduino.keep_alive()
        # sit in an endless loop to receive protocol messages
        await self.receive_loop()  # pub_notification should after receive_loop
        # 在此之后才能发送，publisher先建立起来，消息可以后发

    # The following methods and are called
    # by the gateway base class in its incoming_message_processing
    # method. They overwrite the default methods in the gateway_base.

    # noinspection DuplicatedCode
    def run(self):
        # get the event loop
        # this is for python 3.8
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy())

        try:
            self.event_loop.create_task(
                self.pub_notification('Arduino UNO 已连接',
                                      type="SUCCESS"))
            self.event_loop.run_until_complete(self.main())
            self.logger.debug("arduino thread end")
            self.event_loop.run_until_complete(self.arduino.shutdown())
        except (KeyboardInterrupt, asyncio.CancelledError, RuntimeError):
            pass


export = ArduinoGateway