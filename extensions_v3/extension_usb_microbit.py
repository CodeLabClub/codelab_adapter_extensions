import time
import serial
import json

from codelab_adapter.utils import list_microbit, flash_makecode_file
from codelab_adapter_client.utils import get_adapter_home_path, threaded

# from extension_usb_microbit import MicrobitHelper  # extensions/extension_usb_microbit.py
from codelab_adapter.core_extension import Extension
from codelab_adapter_client.thing import AdapterThing
import threading

# from codelab_adapter.microbit_helper import MicrobitRadioHelper
'''
todo 
    serial 锁
        队列/缓冲
    数字

bug
    为何第一次连接 读不到versions

fifo = deque()
fifo.append(1) # deque([1])
fifo.append(2) # deque([1, 2])
2 in fifo # true
fifo.popleft() # deque([2])
'''


class ThingProxy(AdapterThing):
    def __init__(self, node_instance):
        super().__init__(thing_name="USB micro:bit",
                         node_instance=node_instance)
        # 定长 https://stackoverflow.com/questions/1931589/python-datatype-for-a-fixed-length-fifo
        # The append() and popleft() methods are both atomic.
        # self.write_fifo_queue = deque()  # to microbit
        # self.read_fifo_queue = deque()  # from microbit
        self.lock = threading.Lock()

    def list(self, timeout=5) -> list:
        microbit_ports = list_microbit()  # return
        if not microbit_ports:
            self.node_instance.logger.error("未发现 micro:bit")
            self.node_instance.pub_notification("未发现 micro:bit", type="ERROR")

        return [str(i[0]) for i in microbit_ports]

    # def connect(self, ip, timeout=5):
    def connect(self, id, **kwargs):
        self.port = id
        # self.node_instance.logger.debug(f"args: {kwargs}")
        if not kwargs.get("baudrate", None):
            kwargs["baudrate"] = 115200
        # if not kwargs.get("timeout", None):
        timeout = kwargs["timeout"]  # client输入
        kwargs["timeout"] = 1  # 串口超时时间
        ser = serial.Serial(self.port, **kwargs)
        self.thing = ser
        firmware_path = str(get_adapter_home_path() / "src" /
                            "usb_Microbit_firmware_4v1v2.hex")

        t1 = time.time()
        # time.sleep(0.1)
        while self.node_instance._running:
            if time.time() - t1 >= timeout / 2:
                # 超时没收到version信息， 可能是第一次烧录
                self.node_instance.logger.error("get version timeout")
                ser.close()
                self.node_instance.pub_notification("正在刷入固件...", type="INFO")
                flash_makecode_file(firmware_path)  # todo flash_hex_file
                time.sleep(10)
                return
            # self.send_command(payload="__version__", msgid="query version")
            self.send_command()
            # ser.write(b"version\n")  # 没写进去，microbit没有反应
            data = self.uart_helper()  # timeout, 为何read没东西？ 第一次
            self.node_instance.logger.debug(f"version query reply: {data}")
            if data:
                if data.get("version"):
                    self.node_instance.logger.debug(
                        f"usb microbit firmware -> {data['version']}")
                    version = data.get("version")
                    if version >= "0.4":  # todo 0.5 set radio_03 其他不要动，固件变了
                        self.is_connected = True  # 连接成功
                        self.thing = ser
                        self.node_instance.pub_notification("micro:bit 已连接", type="SUCCESS")
                        self.run_task_forever()
                        return "ok"
                    else:
                        self.thing.close()
                        self.node_instance.pub_notification("正在刷入固件...",
                                                            type="INFO")
                        flash_makecode_file(firmware_path)
                        time.sleep(10)
                        # self.node_instance.pub_notification(self.flash_finished_notification, type="SUCCESS")
                    return  # 只有串口数据是 version_xx才退出循环

    def status(self, **kwargs) -> bool:
        pass

    def disconnect(self):
        self.is_connected = False
        try:
            self.thing.close()
        except Exception:
            pass
        self.thing = None
        self.node_instance.pub_notification(f'{self.node_instance.NODE_ID} 已断开', type="WARNING")

    # 业务代码
    def write(self, content):
        if self.is_connected:
            self.thing.write(content.encode('utf-8'))  # todo 线程安全
            return "ok"

    def _send_microbit_messge(self, data):
        message = self.node_instance.message_template()
        msgid = data.get("msgid")
        message["payload"]["message_id"] = msgid

        output = data.get("output")
        if output:
            # 正常运行了请求的代码
            message["payload"]["content"] = output
            self.node_instance.publish(message)

            # and sensor
            message["payload"]["message_id"] = -1
            message["payload"]["content"] = data["payload"]
            self.node_instance.publish(message)
        else:
            message["payload"]["content"] = data["payload"]
            self.node_instance.publish(message)

    def uart_helper(self):
        '''
        后台任务
        放入缓冲区
        1000个长度
        写入任务
            在同个循环里，避免跨线程
        使用queue跨线程
        
        return
            microbit output
        '''
        try:
            data = self.thing.readline()
            if data:
                data = data.decode()
                try:
                    data = eval(data)  # todo, 来自 Microbit的数据 暂无安全问题
                except (ValueError, SyntaxError) as e:
                    # raise e
                    self.node_instance.logger.error(f"{e}: {data}")
                else:
                    return data
        except UnicodeDecodeError as e:
            self.node_instance.logger.error(e)
        except serial.serialutil.SerialException:
            self.node_instance.pub_notification("micro:bit 连接异常", type="WARNING")
            time.sleep(3)
        except Exception as e:
            self.node_instance.logger.error(e)
            self.node_instance.pub_notification(str(e), type="ERROR")
            # self.node_instance.logger.exception("what!")
            time.sleep(3)

    @threaded
    def run_task_forever(self):
        while self.node_instance._running:
            if self.is_connected:
                # microbit node -> microbit adapter
                # rate = 20
                # time.sleep(1 / rate)
                self.send_command()
                response_from_microbit = self.uart_helper()
                self.node_instance.logger.debug(f'read from microbit: {response_from_microbit}')
                if not response_from_microbit:
                    continue
                if response_from_microbit:
                    # if response_from_microbit.startswith('version_'):
                    '''
                    version = response_from_microbit.get("version")
                    if version and version >= "0.4":
                        # version信息, 状态机 todo
                        continue
                    '''
                    self._send_microbit_messge(response_from_microbit)
            else:
                break

    def send_command(self, payload="0", msgid=-1):
        '''
        payload content
        todo message id 对应
        '''
        self.lock.acquire()
        rate = 10
        time.sleep(1 / rate)
        scratch3_message = {"msgid": msgid, "payload": payload}

        scratch3_message = json.dumps(scratch3_message) + "\r\n"
        scratch3_message_bytes = scratch3_message.encode('utf-8')
        self.node_instance.logger.debug(f'send to microbit: {scratch3_message_bytes}')
        self.thing.write(scratch3_message_bytes)
        self.lock.release()


class MicrobitExtension(Extension):
    '''
    use TokenBucket to limit message rate(pub) https://github.com/CodeLabClub/codelab_adapter_client_python/blob/master/codelab_adapter_client/utils.py#L25
    '''

    NODE_ID = "eim/extension_usb_microbit"
    HELP_URL = "http://adapter.codelab.club/extension_guide/microbit/"
    WEIGHT = 99
    VERSION = "2.0.0"
    DESCRIPTION = "使用 Microbit， 为物理世界编程"

    def __init__(self, **kwargs):  # kwargs 接受启动参数
        super().__init__(
            bucket_token=100,  # 默认是100条 hub模式消息量大
            bucket_fill_rate=100,
            **kwargs)
        self.thing = ThingProxy(self)
        # self.microbitHelper = MicrobitRadioHelper(self)

    def run_python_code(self, code):
        # fork from python extension
        try:
            output = eval(
                code,
                {"__builtins__": None},
                {
                    "thing": self.thing,  # 直接调用方法
                    "connect": self.thing.connect,
                    "disconnect": self.thing.disconnect,
                    "list": self.thing.list,
                })
        except Exception as e:
            output = str(e)
            # 也作为提醒
            self.pub_notification(output, type="ERROR")
        return output

    def extension_message_handle(self, topic, payload):
        self.logger.info(f'python code: {payload["content"]}')
        # message_id = payload.get("message_id")
        python_code = payload["content"]
        # send_command 直接运行 结果呢？ 异步
        # message_id = payload.get("message_id")
        output = self.run_python_code(python_code)
        # 运行命令和其他不一致（异步）
        try:
            output = json.dumps(output)
        except Exception:
            output = str(output)
        if "thing.send_command(" in python_code:
            # payload
            # todo 异步发送
            payload["content"] = "ok"
            message = {"payload": payload}
            self.publish(message)
            
        else:
            payload["content"] = output
            message = {"payload": payload}
            self.publish(message)

    def run(self):
        time.sleep(0.1)

    def terminate(self, **kwargs):
        try:
            self.thing.disconnect()
        except Exception:
            pass
        super().terminate(**kwargs)


export = MicrobitExtension
