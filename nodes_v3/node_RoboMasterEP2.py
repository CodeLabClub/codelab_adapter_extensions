'''
pip install robomasterpy==0.1.1
    node 在外层依赖即可，window mac会提示依赖
# https://robomasterpy.nanmu.me/en/latest/
# https://github.com/nanmu42/robo-playground
'''

import socket
import time
import json
from loguru import logger

from codelab_adapter_client import AdapterNode  # todo 异步插件启动确认
from codelab_adapter_client.thing import AdapterThing

import robomasterpy as rm  # rm.get_broadcast_ip(timeout=1)


class EPProxy(AdapterThing):
    '''
    AdapterThing
        init
            self.thing_name
            self.node_instance
            self.is_connected = False  
            self.thing = None
    python eval code
        connect
        robot.chassis_move(x=-1, z=30)  # thing不存在
        # 分派方法和参数
    '''
    def __init__(self, node_instance):
        # todo pydanic
        super().__init__(thing_name="Robomaster EP",
                         node_instance=node_instance)

    def list(self, timeout=5):
        try:
            broadcast_ip = rm.get_broadcast_ip(timeout=timeout)   # 多个怎么办？
            return [str(broadcast_ip)]
        except socket.timeout:
            # self.node_instance.pub_notification(f"获取设备IP超时({timeout}s)", type="ERROR")
            self.node_instance.pub_notification("未发现 RoboMasterEP", type="ERROR")
            return []
        except Exception as e:
            self.node_instance.pub_notification(
                str(e), type="ERROR")
            return []

    def connect(self, ip, timeout=5):
        # 修改 self.thing， connect失败呢？
        try:
            self.thing = rm.Commander(ip, timeout)
            self.node_instance.pub_notification("RoboMasterEP 已连接", type="SUCCESS")
        except Exception as e:
            self.node_instance.pub_notification(str(e), type="ERROR")

    def status(self, **kwargs) -> bool:
        # check status
        # query thing status, 与设备通信，检查 is_connected 状态，修改它
        pass

    def disconnect(self):
        if self.thing:
            self.thing.close()  # 关闭实例，回收socket资源。注意这个命令并不会发送quit到机甲，避免打扰其他在线的Commander.
            # 允许多个client控制一个机甲
            self.is_connected = False
            self.thing = None

    # 转发
    # cmd.chassis_move(x=-1, z=30)
    # self.thing.chassis_move(x=-1, z=30)
    # robot.thing.chassis_move(x=-1, z=30)


class EPExtension(AdapterNode):
    NODE_ID = "eim/node_RoboMasterEP2"
    HELP_URL = "http://adapter.codelab.club/extension_guide/RoboMasterEP2/"
    DESCRIPTION = "开火！RoboMaster EP"
    VERSION = "2.0.1"  # 处理connect问题

    def __init__(self, **kwargs):
        super().__init__(logger=logger, **kwargs)
        self.ep = EPProxy(self)  # create proxy object

    def run_python_code(self, code):
        try:
            output = eval(
                code,
                {"__builtins__": None},
                {
                    "robot": self.ep.thing,  # 直接调用方法
                    "connect": self.ep.connect,
                    "disconnect": self.ep.disconnect,
                    "list": self.ep.list,
                })
        except Exception as e:
            # logger.exception('what?')
            output = e
        return output

    def extension_message_handle(self, topic, payload):
        # todo 判断是否连接成功，否则报告连接问题

        logger.info(f'code: {payload["content"]}')
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
        while self._running:
            time.sleep(0.5)

    # release robot proxy object
    def terminate(self, **kwargs):
        try:
            if self.ep.is_connected:
                self.ep.disconnect()
        except Exception:
            pass
        super().terminate(**kwargs)


def main(**kwargs):
    try:
        node = EPExtension(**kwargs)
        node.receive_loop_as_thread()
        node.run()
    except Exception as e:
        if node._running:
            node.pub_notification(str(e), type="ERROR")
            time.sleep(0.1)
            node.terminate()


if __name__ == "__main__":
    main()