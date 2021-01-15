import queue
import time
import json
import uuid

import serial
from codelab_adapter.utils import list_microbit, flash_py_hex_file, flash_makecode_file
from codelab_adapter.core_extension import Extension
from codelab_adapter_client.utils import get_adapter_home_path

'''

todo:
    使用makecode构建固件
        command
        query
        event
'''

class MicrobitHelper:
    def __init__(self, extensionInstance=None):
        self.extensionInstance = extensionInstance
        self.logger = extensionInstance.logger
        self.port = None  # 当前连接的port
        self.ser = None
        self.flash_finished_notification = "The firmware is flashed!"


    def connect(self, port, firmware_type, **kwargs):
        '''
        firmware_type
            usb_microbit
            makecode_radio
        '''
        self.port = port
        self.logger.debug(f"args: {kwargs}")
        if self.ser:
            self.ser.close()
            time.sleep(0.2)
        # 默认支持microbit, timeout 默认不超过scratch的积木 5s (3)
        if not kwargs.get("baudrate", None):
            kwargs["baudrate"] = 115200
        if not kwargs.get("timeout", None):
            kwargs["timeout"] = 3
        _ser = serial.Serial(port, **kwargs)
        if firmware_type == "usb_microbit":
            self.send_command(ser = _ser, msgid="query version", payload="__version__") # 子类的方法
            firmware_path = str(get_adapter_home_path() / "src" /"usb_Microbit_firmware_4v1v2.hex")
            try:
                data = self.get_response_from_microbit(_ser)
                self.extensionInstance.logger.debug(f"query version(reply) -> {data}")
                # none?
                if data.get("version") and data.get("version") >= "0.4":
                    self.extensionInstance.logger.debug(f"microbit firmware -> {data['version']}")   
                else:
                    self.extensionInstance.pub_notification("flashing new firmware...",type="INFO") 
                    _ser.close()
                    flash_py_hex_file(firmware_path)
                    # flash_usb_microbit(firmware_path)
                    # flash_usb_microbit是非阻塞的
                    # https://github.com/ntoll/uflash/blob/master/tests/test_uflash.py
                    # self.extensionInstance.pub_notification(self.flash_finished_notification, type="SUCCESS")
                    return
            except Exception as e:
                self.extensionInstance.logger.error(e)
                # self.extensionInstance.logger.exception("!!!")
                _ser.close()
                self.extensionInstance.pub_notification("flashing firmware...", type="INFO")
                flash_py_hex_file(firmware_path)
                # self.extensionInstance.pub_notification(self.flash_finished_notification, type="SUCCESS")
                raise e

        if firmware_type == "makecode_radio":
            self.write("version\n",ser=_ser)
            firmware_path = str(get_adapter_home_path() / "src" /"makecode_radio_adapter.hex")
            try:
                data = self.readline(_ser)
                self.extensionInstance.logger.debug(f"makecode_radio uart reply: {data}")
                if type(data)==str and data >= "0.4": # todo 0.4 set radio_03 其他不要动，固件变了
                    self.extensionInstance.logger.debug(f"makecode radio firmware -> {data}")   
                else:
                    # flash
                    _ser.close()
                    self.extensionInstance.pub_notification("flashing firmware...",type="ERROR") 
                    flash_makecode_file(firmware_path)
                    # self.extensionInstance.pub_notification(self.flash_finished_notification, type="SUCCESS")
                    return
            except Exception as e:
                self.extensionInstance.logger.error(e)
                _ser.close()
                self.extensionInstance.pub_notification("flashing firmware...",type="ERROR") 
                flash_makecode_file(firmware_path)
                # self.extensionInstance.pub_notification(self.flash_finished_notification, type="SUCCESS")
                raise e # 使UI断开
        
        self.ser = _ser
        # query version
        if self.ser.name:
            self.extensionInstance.pub_notification("micro:bit Connected!",
                                                    type="SUCCESS")
            return "ok"

    def disconnect(self, **kwargs):
            self.extensionInstance.pub_notification("micro:bit disconnected!")
            time.sleep(0.1)
            self.extensionInstance.terminate()

    def list_ports(self):
        microbit_ports = list_microbit()  # return
        if not microbit_ports:
            self.logger.error("No micro:bit found")
            self.extensionInstance.pub_notification("No micro:bit found",
                                                    type="ERROR")

        return microbit_ports

    # scan message type
    def update_ports(self):
        ports = [i[0] for i in self.list_ports()]
        message = self.extensionInstance.message_template()
        message["payload"]["content"] = {
            "ports": ports,
        }
        self.extensionInstance.publish(message)
        return "ok"

    def write(self, content, ser=None):
        if not ser:
            ser = self.ser
        if ser:
            ser.write(content.encode('utf-8'))
            # time.sleep(0.1) # 避免遗漏消息
            return "ok"
        else:
            self.extensionInstance.pub_notification("Please connect micro:bit!", type="ERROR")


    def readline(self, ser=None):
        if not ser:
            ser = self.ser
        if ser:
            content = ser.readline()  # timeout
            if content:
                content_str = content.decode()
                return content_str.strip()
        else:
            self.extensionInstance.pub_notification("Please connect micro:bit!", type="ERROR")
            time.sleep(1)

class UsbMicrobitHelper(MicrobitHelper):
    def __init__(self, extensionInstance):
        super().__init__(extensionInstance)

    def send_command(self, ser = None, msgid=-1, payload="0"):
        '''
        总是写入
        '''
        if not self.extensionInstance.q.empty():
            (python_code, message_id) = self.extensionInstance.q.get()
            scratch3_message = {
                "msgid": message_id,
                "payload": python_code
            }
        else:
            scratch3_message = {
                "msgid": msgid,
                "payload": payload
            }
        scratch3_message = json.dumps(scratch3_message) + "\r\n"
        scratch3_message_bytes = scratch3_message.encode('utf-8')
        self.logger.debug(scratch3_message_bytes)
        if not ser:
            ser = self.ser
        ser.write(scratch3_message_bytes)

    def get_response_from_microbit(self, ser=None):
        if not ser:
            ser = self.ser
        try:
            data = ser.readline()
            if data:
                data = data.decode()
                try:
                    data = eval(data)  # todo, 来自 Microbit的数据 暂无安全问题
                except (ValueError, SyntaxError) as e:
                    # raise e
                    self.extensionInstance.logger.error(f"{e}: {data}")
                else:
                    return data
        except UnicodeDecodeError as e:
            # raise e
            self.extensionInstance.logger.error(e)
        except:
            self.extensionInstance.logger.error(e)

class UsbMicrobitProxy(Extension):
    '''
    use TokenBucket to limit message rate(pub) https://github.com/CodeLabClub/codelab_adapter_client_python/blob/master/codelab_adapter_client/utils.py#L25
    '''

    NODE_ID = "eim/extension_usb_microbit"
    HELP_URL = "http://adapter.codelab.club/extension_guide/microbit/"
    WEIGHT = 99
    DESCRIPTION = "使用 Microbit， 为物理世界编程"

    def __init__(self, **kwargs):
        super().__init__(bucket_token=100,
                         bucket_fill_rate=100, **kwargs)
        self.microbitHelper = UsbMicrobitHelper(self)
        self.q = queue.Queue()

    def run_python_code(self, code):
        # fork from python extension
        try:
            output = eval(code, {"__builtins__": None}, {
                "microbitHelper": self.microbitHelper,
            })
        except Exception as e:
            output = str(e)
            self.pub_html_notification(output, type="ERROR")
        return output

    def extension_message_handle(self, topic, payload):
        '''
            test: codelab-message-pub -j '{"topic":"scratch/extensions/command","payload":{"node_id":"eim/extension_usb_microbit", "content":"display.show(\"c\")"}}'
        '''
        self.logger.info(f'python code: {payload["content"]}')
        message_id = payload.get("message_id")
        python_code = payload["content"]
        if "microbitHelper" in python_code:
            output = self.run_python_code(python_code)
            payload["content"] = output
            message = {"payload": payload}
            self.publish(message)
        else:
            self.q.put((python_code, message_id))

    def run(self):
        while self._running:
            if self.microbitHelper.ser:
                try:
                    self.microbitHelper.send_command()
                    # 一读一写 比较稳定, todo: CQRS , todo makecode create hex
                    response_from_microbit = self.microbitHelper.get_response_from_microbit(
                    )
                    if response_from_microbit:
                        message = self.message_template()
                        msgid = response_from_microbit.get("msgid")
                        message["payload"]["message_id"] = msgid

                        output = response_from_microbit.get("output")
                        if output:
                            # 正常运行了请求的代码
                            message["payload"]["content"] = output
                            self.publish(message)

                            # and sensor
                            message["payload"]["message_id"] = -1
                            message["payload"]["content"] = response_from_microbit["payload"]
                            self.publish(message)
                        else:
                            message["payload"]["content"] = response_from_microbit["payload"]
                            self.publish(message)
                    rate = 20
                    time.sleep(1 / rate)
                    self.logger.debug("0.1")
                except Exception as e:
                    # self.logger.exception("!!!")
                    self.pub_notification(str(e), type="ERROR")
                    time.sleep(0.1)
                    self.terminate()
            else:
                time.sleep(0.5)

    def terminate(self):
        try:
            if self.microbitHelper.ser:
                self.microbitHelper.ser.close()
        except Exception as e:
            self.logger.error(e)
        super().terminate()
            
            

export = UsbMicrobitProxy
