'''
pip install alphamini==1.1.0
https://web.ubtrobot.com/mini-python-sdk/guide.html
https://github.com/marklogg/mini_demo.git

内置行为: https://web.ubtrobot.com/mini-python-sdk/additional.html
'''

import asyncio
from loguru import logger

from codelab_adapter_client import AdapterNodeAio  # todo 异步插件启动确认
from codelab_adapter_client.thing import AdapterThing

import mini.mini_sdk as MiniSdk
from mini.apis.base_api import MiniApiResultType
from mini.dns.dns_browser import WiFiDevice
from mini.apis.api_sound import StartPlayTTS, StopPlayTTS, ControlTTSResponse
from mini.apis.api_action import PlayAction, PlayActionResponse
from mini.apis.api_action import GetActionList, GetActionListResponse, RobotActionType
from mini.apis.api_setup import StartRunProgram
from mini.apis.api_action import MoveRobot, MoveRobotDirection, MoveRobotResponse
from mini.apis.api_expression import PlayExpression, PlayExpressionResponse
from mini.apis.api_behavior import StartBehavior, StopBehavior

from mini.apis.api_sence import FaceAnalysis, FaceAnalyzeResponse
from mini.apis.api_sence import FaceDetect, FaceDetectResponse
from mini.apis.api_sence import FaceRecognise, FaceRecogniseResponse
# 使用异步节点

# 红外测距
from mini.apis.api_sence import GetInfraredDistance, GetInfraredDistanceResponse
# 物体识别 水果 鲜花 手势
from mini.apis.api_sence import ObjectRecognise, RecogniseObjectResponse, ObjectRecogniseType


class RobotProxy(AdapterThing):
    '''
    AdapterThing
        init
            self.thing_name
            self.node_instance
            self.is_connected = False  
            self.thing = None
    '''
    def __init__(self, node_instance):
        # todo pydanic
        super().__init__(thing_name="悟空机器人(alphamini)", node_instance=node_instance)

    async def list(self):
        # 需要在UI中填入序列号连接
        # 课堂 在UI输入序列号连接
        # self._ensure_connect()
        return

        '''
        results = await MiniSdk.get_device_list(10)  # 无法搜到
        # print(results)
        return [str(i) for i in results]
        '''

    async def connect(self, robot_name):
        # 修改 self.thing
        if self.is_connected:
            return f"{self.thing_name} already connected"
        else:
            # robot_name = kwargs.get("robot_name")  # todo
            self.thing: WiFiDevice = await MiniSdk.get_device_by_name(
                robot_name, 10)
            if self.thing:
                is_success = await MiniSdk.connect(self.thing)
                if is_success:
                    self.is_connected = True
                    # (resultType, response) = await StartRunProgram().execute() #
                    await MiniSdk.enter_program()
                    # await self.say()
                    # await asyncio.sleep(100)
                    return is_success

    def status(self, **kwargs) -> bool:
        # check status
        # query thing status, 与设备通信，检查 is_connected 状态，修改它
        pass
    
    # disconnect, 兼容
    async def quit(self):
        self._ensure_connect()
        await MiniSdk.quit_program()
        await MiniSdk.release()
        self.is_connected = False
        self.thing = None

    async def disconnect(self):
        return await self.quit()

    ################## 以下是业务逻辑

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

    ### 人脸api: https://github.com/marklogg/mini_demo/blob/42cacfa5c8e8a47ed343ab61c691c1973b17e742/test/test_sence.py#L18
    async def face_detect(self, timeout=10):
        block: FaceDetect = FaceDetect(timeout=timeout)
        # response: FaceDetectResponse
        (resultType, response) = await block.execute()
        logger.debug(f'test_face_detect result: {response}')
    
        assert resultType == MiniApiResultType.Success, 'face_detect timetout'
        assert response is not None and isinstance(response, FaceDetectResponse), 'face_detect result unavailable'
        assert response.isSuccess, 'face_detect failed'

        return response.count # 人脸个数

    async def face_analysis(self, timeout=10):
        # https://github.com/marklogg/mini_demo/blob/42cacfa5c8e8a47ed343ab61c691c1973b17e742/test/test_sence.py#L43
        block: FaceAnalysis = FaceAnalysis(timeout=timeout)
        # response: FaceAnalyzeResponse
        (resultType, response) = await block.execute()

        logger.debug(f'test_face_analysis result: {response}')
        # print('code = {0}, error={1}'.format(response.resultCode, errors.get_vision_error_str(response.resultCode)))

        assert resultType == MiniApiResultType.Success, 'face_analysis timetout'
        assert response is not None and isinstance(response, FaceAnalyzeResponse), 'face_analysis result unavailable'
        assert response.isSuccess, 'face_analysis failed'
        # gender: 小于50为女性，大于50为男性
        return response  # {"age": 24, "gender": 99, "height": 238, "width": 238}

    async def face_recognise(self, timeout=10):
        # https://github.com/marklogg/mini_demo/blob/42cacfa5c8e8a47ed343ab61c691c1973b17e742/test/test_sence.py#L182
        # response : FaceRecogniseResponse
        (resultType, response) = await FaceRecognise(timeout=timeout).execute()

        logger.debug(f'face_recognise result: {response}')

        assert resultType == MiniApiResultType.Success, 'face_recognise timetout'
        assert response is not None and isinstance(response,
                                                FaceRecogniseResponse), 'face_recognise result unavailable'
        assert response.isSuccess, 'face_recognise failed'
        return response.faceInfos # id name 

    # 测试获取红外探测距离
    async def get_infrared_distance(self):
        (resultType, response) = await GetInfraredDistance().execute()

        # print(f'test_get_infrared_distance result: {response}')

        assert resultType == MiniApiResultType.Success, 'get_infrared_distance timetout'
        assert response is not None and isinstance(response,
                                                GetInfraredDistanceResponse), 'get_infrared_distance result unavailable'
        assert response.distance > 0, 'get_infrared_distance failed'
        return response.distance

    # 物体识别
    async def recognise_gesture(self, timeout=10):
        """测试物体(手势)识别
        """
        # object_type: 支持FLOWER, FRUIT, GESTURE 三类物体
        block: ObjectRecognise = ObjectRecognise(object_type=ObjectRecogniseType.GESTURE, timeout=timeout)
        # response : RecogniseObjectResponse
        (resultType, response) = await block.execute()

        logger.debug(f'recognise_gesture result: {response}')

        assert resultType == MiniApiResultType.Success, 'recognise_gesture timetout'
        assert response is not None and isinstance(response,
                                                RecogniseObjectResponse), 'recognise_gesture result unavailable'
        assert response.isSuccess, 'recognise_gesture failed'
        return response.objects

    async def recognise_fruit(self, timeout=10):
        """测试物体(水果)识别
        """
        # object_type: 支持FLOWER, FRUIT, GESTURE 三类物体
        block: ObjectRecognise = ObjectRecognise(object_type=ObjectRecogniseType.FRUIT, timeout=timeout)
        # response : RecogniseObjectResponse
        (resultType, response) = await block.execute()

        logger.debug(f'test_object_recognise_fruit result: {response}')

        assert resultType == MiniApiResultType.Success, 'recognise_fruit timetout'
        assert response is not None and isinstance(response,
                                                RecogniseObjectResponse), 'recognise_fruit result unavailable'
        assert response.isSuccess, 'recognise_fruit failed'
        return response.objects

    # 语音识别
    # https://github.com/marklogg/mini_demo/blob/42cacfa5c8e8a47ed343ab61c691c1973b17e742/test/test_event.py#L16 

class MiniExtension(AdapterNodeAio):
    NODE_ID = "eim/node_alphamini"
    HELP_URL = "https://adapter.codelab.club/extension_guide/node_alphamini/"
    DESCRIPTION = "悟空是一只伪装成机器人的猴子"
    VERSION = "1.2.0"

    def __init__(self, **kwargs):
        super().__init__(logger=logger, **kwargs)
        self.thing = RobotProxy(self)  # create robot proxy object

    async def run_python_code(self, code):
        try:
            output = await eval(
                code,
                {"__builtins__": None},
                {
                    # "api_instance": self.thing.api_instance,
                    "robot": self.thing
                })
        except Exception as e:
            # todo 完整错误
            # logger.exception('what?')
            output = e
        return output

    async def extension_message_handle(self, topic, payload):
        # todo 判断是否连接成功，否则报告连接问题

        logger.info(f'code: {payload["content"]}')
        # message_id = payload.get("message_id")
        python_code = payload["content"]
        output = await self.run_python_code(python_code)
        payload["content"] = str(output)
        message = {"payload": payload}
        await self.publish(message)

    # release robot proxy object
    async def terminate(self, **kwargs):
        if self.thing.is_connected:
            await self.thing.disconnect()
        await super().terminate(**kwargs)


def main(**kwargs):
    try:
        node = MiniExtension(**kwargs)
        asyncio.run(node.receive_loop())
    except KeyboardInterrupt:
        if node._running:
            asyncio.run(node.terminate())

if __name__ == "__main__":
    main()