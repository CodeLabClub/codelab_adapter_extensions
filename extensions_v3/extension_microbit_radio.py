import time
import serial
import json
from collections import deque
import threading

from codelab_adapter.utils import list_microbit, flash_makecode_file
from codelab_adapter_client.utils import get_adapter_home_path, threaded

# from extension_usb_microbit import MicrobitHelper  # extensions/extension_usb_microbit.py
from codelab_adapter.core_extension import Extension
from codelab_adapter_client.thing import AdapterThing

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
        super().__init__(thing_name="micro:bit-radio",
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
        kwargs["timeout"] = 0.5  # 串口超时时间
        ser = serial.Serial(self.port, **kwargs)

        firmware_path = str(get_adapter_home_path() / "src" /
                            "makecode_radio_adapter.hex")
        t1 = time.time()
        # time.sleep(0.1)
        while self.node_instance._running:
            if time.time() - t1 >= timeout / 2:
                # 超时没收到version信息， 可能是第一次烧录
                self.node_instance.logger.error("get version timeout")
                ser.close()
                self.node_instance.pub_notification("正在刷入固件...", type="INFO")
                flash_makecode_file(firmware_path)
                time.sleep(10)
                return
            ser.write(b"version\n")  # 没写进去，microbit没有反应
            data = ser.readline()  # timeout
            if data:
                self.node_instance.logger.debug(f"version query reply: {data}")
                data = data.decode().strip()
                if data.startswith("version_"):
                    version = data.split('version_')[-1]
                    self.node_instance.logger.debug(
                        f"makecode radio firmware -> {version}")
                    if version >= "0.5":  # todo 0.5 set radio_03 其他不要动，固件变了
                        self.is_connected = True  # 连接成功
                        self.thing = ser
                        if self.thing.name:
                            self.node_instance.pub_notification(
                                "micro:bit 已连接", type="SUCCESS")
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
        # 不要try，暴露问题
        self.is_connected = False  # todo 不需要这个，使用thing 是否存在即可
        try:
            self.thing.close()
        except Exception:
            pass
        self.thing = None
        self.node_instance.pub_notification(f'{self.node_instance.NODE_ID} 已断开', type="WARNING")  # 切断插件？

    # 业务
    def write(self, content):
        if self.is_connected:
            self.lock.acquire()  # todo queue？ 好像某些 windows 会导致 microbit死掉 好像是发的东西不对，在 microbit 观察下
            self.thing.write(content.encode('utf-8'))  # todo 线程安全
            # time.sleep(0.1) # 避免遗漏消息
            self.thing.flush()
            # 前端使用等待的
            self.lock.release()
            return "ok"
            

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
        if self.is_connected:
            try:
                # 写入队列和读出队列
                # write from queue
                data = self.thing.readline()  # timeout?
                self.node_instance.logger.debug(f"readline: {data}")
                if data:
                    data_str = data.decode()
                    return data_str.strip()
            except Exception as e:
                # self.is_connected = False
                # self.thing = None
                self.node_instance.logger.error(e)
                self.node_instance.pub_notification(str(e), type="ERROR")
                time.sleep(0.1)  # 提示设备未连接
                # 强行拔掉后，自行退出
                self.node_instance.terminate()  # 需要插件退出吗？

    @threaded
    def run_task_forever(self):
        while self.node_instance._running:
            if self.is_connected:
                # microbit node -> microbit adapter
                response_from_microbit = self.uart_helper()
                if response_from_microbit:
                    if response_from_microbit.startswith('version_'):
                        # version信息, 状态机 todo
                        pass
                    else:
                        message = self.node_instance.message_template()
                        message["payload"]["content"] = response_from_microbit
                        # 来自radio的消息，与控制消息区分开
                        message["payload"]["message_type"] = 'radio_message'
                        self.node_instance.publish(message)
            else:
                break


class MicrobitRadioProxy(Extension):
    '''
    use TokenBucket to limit message rate(pub) https://github.com/CodeLabClub/codelab_adapter_client_python/blob/master/codelab_adapter_client/utils.py#L25
    '''

    NODE_ID = "eim/extension_microbit_radio"
    HELP_URL = "http://adapter.codelab.club/extension_guide/microbit_radio/"
    WEIGHT = 98
    VERSION = "2.0.0"  # 简化makecode对字符串的处理，移除\r
    DESCRIPTION = "Microbit radio 信号中转站"

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
        '''
            test: codelab-message-pub -j '{"topic":"scratch/extensions/command","payload":{"node_id":"eim/extension_microbit_radio", "content":"thing.write(\"c\")"}}'
        '''
        self.logger.info(f'python code: {payload["content"]}')
        # message_id = payload.get("message_id")
        python_code = payload["content"]
        output = self.run_python_code(python_code)
        try:
            output = json.dumps(output)
        except Exception:
            output = str(output)
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


export = MicrobitRadioProxy
