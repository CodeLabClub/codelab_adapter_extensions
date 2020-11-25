'''
pip install alphamini
https://web.ubtrobot.com/mini-python-sdk/guide.html
https://github.com/marklogg/mini_demo.git

内置行为: https://web.ubtrobot.com/mini-python-sdk/additional.html

todo
    内置？
        插件启动确认
'''

import time
import asyncio
from loguru import logger

from codelab_adapter_client import AdapterNodeAio # todo 异步插件启动确认

import mini.mini_sdk as MiniSdk
from mini.dns.dns_browser import WiFiDevice
from mini.apis.api_sound import StartPlayTTS, StopPlayTTS, ControlTTSResponse
from mini.apis.api_action import PlayAction, PlayActionResponse
from mini.apis.api_action import GetActionList, GetActionListResponse, RobotActionType
from mini.apis.api_setup import StartRunProgram
from mini.apis.api_action import MoveRobot, MoveRobotDirection, MoveRobotResponse
from mini.apis.api_expression import PlayExpression, PlayExpressionResponse
from mini.apis.api_behavior import StartBehavior, StopBehavior

# 使用异步节点


class RobotProxy:
    def __init__(self, node=None):
        self.node = node
        self.is_connected = False  # todo 装饰器， 确认某件事才往下，否则返回错误信息， require connect，每次确保某件事发生
        self.robot_name = None
        self.robot = None

    def _ensure_connect(self):
        if not self.is_connected:
            raise Exception("Device not connected!")

    async def list(self):
        self._ensure_connect()
        results = await MiniSdk.get_device_list(10)
        print(results)
        return [str(i) for i in results]

    async def connect(self, robot_name="0447"):
        if self.is_connected:
            return "Device already connected"
        self.robot: WiFiDevice = await MiniSdk.get_device_by_name(
            robot_name, 10)
        if self.robot:
            is_success = await MiniSdk.connect(self.robot)
            if is_success:
                self.is_connected = True
                # (resultType, response) = await StartRunProgram().execute() #
                await MiniSdk.enter_program()
                # await self.say()
                # await asyncio.sleep(100)
                return is_success

    async def GetActionList(self):
        self._ensure_connect()
        # robot.play(name="bow",speed="slow",operation="start")
        block: GetActionList = GetActionList(action_type=RobotActionType.INNER)
        # response:GetActionListResponse
        (resultType, response) = await block.execute()
        return response

    async def play_action(self, **kwargs):
        '''
        https://web.ubtrobot.com/mini-python-sdk/additional.html#id2
        https://web.ubtrobot.com/mini-python-sdk/additional.html#id3

        010 打招呼
        011 点头
        012 俯卧撑
        013 武术
        014 太极
        027 坐下
        031 蹲下
        017 举双手
        015 欢迎
        037 摇头
        Surveillance_001 打招呼
        Surveillance_004 飞吻
        Surveillance_006 卖萌
        action_016 再见
        action_014 邀请
        action_005 点赞
        '''
        self._ensure_connect()
        block: PlayAction = PlayAction(**kwargs)
        # response: PlayActionResponse
        (resultType, response) = await block.execute()
        return response

    async def play_expression(self, **kwargs):
        '''
        codemao9 打喷嚏
        codemao13	疑问
        codemao16	贱贱的笑
        codemao20	眨眼
        emo_020	发呆
        codemao19 爱心
        '''
        self._ensure_connect()
        # https://web.ubtrobot.com/mini-python-sdk/additional.html#id4
        block: PlayExpression = PlayExpression(**kwargs)
        # response: PlayExpressionResponse
        (resultType, response) = await block.execute()
        return response

    async def play_behavior(self, **kwargs):
        '''
        custom_0035 生日快乐
        dance_0008 虫儿飞
        '''
        self._ensure_connect()
        # https://web.ubtrobot.com/mini-python-sdk/additional.html#id4
        block = StartBehavior(**kwargs)
        if kwargs.get("is_serial"):
            (resultType, response) = await block.execute()
            return response
        else:
            return await block.execute()

    async def stop_behavior(self, **kwargs):
        '''
        custom_0035 生日快乐
        dance_0008 虫儿飞
        '''
        self._ensure_connect()
        # https://web.ubtrobot.com/mini-python-sdk/additional.html#id4
        block = StopBehavior(**kwargs)
        (resultType, response) = await block.execute()
        return response

    async def move(self, step=1, direction="FORWARD"):
        '''
        
        FORWARD : 向前
        BACKWARD : 向后
        LEFTWARD : 向左
        RIGHTWARD : 向右
        '''
        self._ensure_connect()
        block: MoveRobot = MoveRobot(step=step,
                                     direction=MoveRobotDirection[direction])
        (resultType, response) = await block.execute()
        return response

    async def bow(self):
        self._ensure_connect()
        # robot.play(name="bow",speed="slow",operation="start")
        pass

    async def say(self, **kwargs):
        self._ensure_connect()
        block: StartPlayTTS = StartPlayTTS(**kwargs)
        # 返回元组, response是个ControlTTSResponse
        (resultType, response) = await block.execute()

    # 判断函数决定同步异步
    async def quit(self):
        self._ensure_connect()
        await MiniSdk.quit_program()
        await MiniSdk.release()
        self.is_connected = False

class MiniExtension(AdapterNodeAio):
    NODE_ID = "eim/node_alphamini"
    HELP_URL = "https://adapter.codelab.club/extension_guide/node_alphamini/"
    DESCRIPTION = "悟空机器人"

    def __init__(self):
        super().__init__(logger=logger)
        self.robot = RobotProxy(self)  # create robot proxy object

    async def run_python_code(self, code):
        try:
            output = await eval(
                code,
                {"__builtins__": None},
                {
                    # "api_instance": self.robot.api_instance,
                    "robot": self.robot
                })
        except Exception as e:
            # todo 完整错误
            # logger.exception('what?')
            output = e
        return output

    async def extension_message_handle(self, topic, payload):
        # todo 判断是否连接成功，否则报告连接问题

        self.logger.info(f'code: {payload["content"]}')
        message_id = payload.get("message_id")
        python_code = payload["content"]
        output = await self.run_python_code(python_code)
        payload["content"] = str(output)
        message = {"payload": payload}
        await self.publish(message)

    # release robot proxy object
    async def terminate(self, **kwargs):
        if self.robot.is_connected:
            await self.robot.quit()
        await super().terminate(**kwargs)


if __name__ == "__main__":
    try:
        node = MiniExtension()
        asyncio.run(node.receive_loop())
    except KeyboardInterrupt:
        if node.robot.is_connected:
            # asyncio.run?
            asyncio.run(node.robot.quit())
            print("robot quit!")
            # node.robot.quit() # todo run async
        if node._running:
            asyncio.run(node.terminate())
            # Clean up before exiting.
