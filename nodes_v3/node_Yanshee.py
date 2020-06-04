'''
https://github.com/UBTEDU/Yan_ADK
http://192.168.31.109:9090/v1/ui/#!/devices/get_devices_battery
https://app.swaggerhub.com/apis-docs/UBTEDU/apollo_cn/1.0.0#/devices/getDevicesVersions

todo 
    使用rest api， 不用 openadk

调试技巧
    直接使用python 在terminal里运行 node 插件
'''
import sys
import time
import os  # env

from loguru import logger
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import get_or_create_node_logger_dir, install_requirement
from pprint import pprint

node_logger_dir = get_or_create_node_logger_dir()
debug_log = str(node_logger_dir / "debug.log")
logger.add(debug_log, rotation="1 MB", level="DEBUG")


class Robot:
    def __init__(self, node=None):
        self.node = node
        self.configuration = None  # 标识是否连接
        self.is_connected = False

    def connect(self, robot_ip="raspberrypi.local"):
        # 如果未完成，则对robot的调用都弹出提醒
        self.configuration = openadk.Configuration()  # openadk global
        self.configuration.host = f'http://{robot_ip}:9090/v1'  # /ui
        if self.ping_robot() == "online":
            if self.node:
                self.node.pub_notification("Device(Yanshee) Connected!",
                                           type="SUCCESS")  # 由一个积木建立连接到时触发
            self.is_connected = True
            return True

    # todo 装饰器 require connect
    def ping_robot(self):
        if not self.configuration:
            return
        self.devices_api_instance = openadk.DevicesApi(
            openadk.ApiClient(self.configuration))
        try:
            # Get system's battery information
            api_response = self.devices_api_instance.get_devices_battery()
            logger.debug(api_response)
            return "online"
        except ApiException as e:  # global
            error_message = f"Exception when calling DevicesApi->get_devices_battery: {str(e)}"
            logger.error(error_message)
            if node:
                node.pub_notification(error_message, type="ERROR")

    def play(
        self,
        name="wave",  # GetUp, Hug, Bow , HappyBirthday, Forward Backward OneStepForward TurnLeft TurnRight
        operation='start',
        direction='both',
        speed="fast"):  # ['start', 'pause', 'resume', 'stop']

        if not self.configuration:
            return
        motion_api_instance = MotionsApi(openadk.ApiClient(self.configuration))
        timestamp = int(time.time())
        kw = {"name": name, "speed": speed, "repeat": 1}
        if direction:
            kw["direction"] = direction
        motion = MotionsParameter(**kw)
        body = MotionsOperation(motion=motion,
                                operation=operation,
                                timestamp=timestamp)
        try:
            ret = motion_api_instance.put_motions(body)
        except ApiException as e:
            error_message = f"Exception when calling DevicesApi->get_devices_battery: {str(e)}"
            logger.error(error_message)
            if node:
                node.pub_notification(error_message, type="ERROR")
        # assert ret.code == 0
        return ret

    def bow(self):
        if not self.configuration:
            return
        self.play(name="bow", direction="", speed="slow", operation="start")

    def say(self, content="你好"):
        if not self.configuration:
            return
        timestamp = int(time.time())
        api_instance = openadk.VoiceApi(openadk.ApiClient(self.configuration))
        body = openadk.VoiceTTSStr(content)  # VoiceTTSStr |
        api_response = api_instance.put_voice_tts(body)


class YansheeNode(AdapterNode):
    NODE_ID = "eim/node_Yanshee"
    REQUIREMENTS = ["https://github.com/UBTEDU/Yan_ADK/archive/latest.tar.gz"]
    HELP_URL = "https://adapter.codelab.club/extension_guide/yanshee/"
    DESCRIPTION = "基于树莓派的开放机器人平台"

    def __init__(self):
        super().__init__(logger=logger)
        self.NODE_ID = self.generate_node_id(__file__)
        self.robot = Robot(self)

    def _import_requirement_or_import(self):
        requirement = self.REQUIREMENTS
        try:
            import openadk
        except ModuleNotFoundError:
            self.pub_notification(f'try to install {" ".join(requirement)}...')
            install_requirement(requirement)
            self.pub_notification(f'{" ".join(requirement)} installed!')

        import openadk
        from openadk.rest import ApiException
        from openadk.models.motions_parameter import MotionsParameter
        from openadk.models.motions_operation import MotionsOperation
        from openadk.api.motions_api import MotionsApi

        global openadk, ApiException, MotionsParameter, MotionsOperation, MotionsApi

    def run_python_code(self, code):
        try:
            output = eval(
                code,
                {"__builtins__": None},
                {
                    # "api_instance": self.robot.api_instance,
                    "robot": self.robot
                })
        except Exception as e:
            output = e
        return output

    def extension_message_handle(self, topic, payload):
        # todo 判断是否连接成功，否则报告连接问题

        self.logger.info(f'code: {payload["content"]}')
        message_id = payload.get("message_id")
        python_code = payload["content"]

        # 检查是否连接
        if (not self.robot.is_connected) and ("connect" not in python_code):
            self.pub_notification("Please connect Device(Yanshee)",
                                  type="WARNING")
            return

        output = self.run_python_code(python_code)
        payload["content"] = str(output)
        message = {"payload": payload}
        self.publish(message)

    def run(self):
        self._import_requirement_or_import()
        while self._running:
            time.sleep(0.5)


if __name__ == "__main__":
    try:
        node = YansheeNode()
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        if node._running:
            node.terminate()  # Clean up before exiting.