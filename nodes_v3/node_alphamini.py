'''
pip install alphamini
https://web.ubtrobot.com/mini-python-sdk/guide.html
https://github.com/marklogg/mini_demo.git

内置行为: https://web.ubtrobot.com/mini-python-sdk/additional.html

todo
    内置？
'''

import sys
import time
import os  # env

from codelab_adapter_client import AdapterNodeAio

import asyncio
import logging

import mini.mini_sdk as MiniSdk
from mini.dns.dns_browser import WiFiDevice
from mini.apis.api_sound import StartPlayTTS, StopPlayTTS, ControlTTSResponse
from mini.apis.api_action import PlayAction, PlayActionResponse
from mini.apis.api_action import GetActionList, GetActionListResponse, RobotActionType
from mini.apis.api_setup import StartRunProgram
from mini.apis.api_action import MoveRobot, MoveRobotDirection, MoveRobotResponse
from mini.apis.api_expression import PlayExpression, PlayExpressionResponse

# 使用异步节点


class Robot:
    def __init__(self, node=None):
        self.node = node
        self.is_connected = False
        self.robot_name = None
        self.robot = None

    async def list(self):
        results = await MiniSdk.get_device_list(10)
        print(results)
        return [str(i) for i in results]

    async def connect(self, robot_name="0447"):
        self.robot: WiFiDevice = await MiniSdk.get_device_by_name(
            robot_name, 10)
        if self.robot:
            is_success = await MiniSdk.connect(self.robot)
            if is_success:
                # (resultType, response) = await StartRunProgram().execute() #
                await MiniSdk.enter_program()
                # await self.say()
                # await asyncio.sleep(100)
                return is_success

    async def GetActionList(self):
        # robot.play(name="bow",speed="slow",operation="start")
        block: GetActionList = GetActionList(action_type=RobotActionType.INNER)
        # response:GetActionListResponse
        (resultType, response) = await block.execute()
        return response

    async def play_action(self, action_name="010"):
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
        block: PlayAction = PlayAction(action_name=action_name)
        # response: PlayActionResponse
        (resultType, response) = await block.execute()
        return response

    async def play_expression(self, express_name="codemao13"):
        '''
        codemao9 打喷嚏
        codemao13	疑问
        codemao16	贱贱的笑
        codemao20	眨眼
        emo_020	发呆
        codemao19 爱心
        '''
        # https://web.ubtrobot.com/mini-python-sdk/additional.html#id4
        block: PlayExpression = PlayExpression(express_name=express_name)
        # response: PlayExpressionResponse
        (resultType, response) = await block.execute()
        return response

    async def move(self, step=1, direction="FORWARD"):
        '''
        FORWARD : 向前
        BACKWARD : 向后
        LEFTWARD : 向左
        RIGHTWARD : 向右
        '''
        block: MoveRobot = MoveRobot(step=step,
                                     direction=MoveRobotDirection[direction])
        (resultType, response) = await block.execute()
        return response

    async def bow(self):
        # robot.play(name="bow",speed="slow",operation="start")
        pass

    async def say(self, content="你好"):
        block: StartPlayTTS = StartPlayTTS(text=content)
        # 返回元组, response是个ControlTTSResponse
        (resultType, response) = await block.execute()

    # 判断函数决定同步异步
    async def quit(self):
        await MiniSdk.quit_program()
        await MiniSdk.release()

    async def loop(self):
        while True:
            await asyncio.sleep(1)


class MiniExtension(AdapterNodeAio):
    NODE_ID = "eim/node_alphamini"
    HELP_URL = "https://adapter.codelab.club/extension_guide/node_alphamini/"
    DESCRIPTION = "悟空机器人"

    def __init__(self):
        super().__init__()
        self.robot = Robot(self)

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


if __name__ == "__main__":
    try:
        node = MiniExtension()
        asyncio.run(node.receive_loop())
    except KeyboardInterrupt:
        if node._running:
            asyncio.run(node.terminate())
            # Clean up before exiting.
