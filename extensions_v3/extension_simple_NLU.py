'''
inspired by https://github.com/rizal72/Cozmo-Voice-Commands/blob/master/cvc/cozmo_voice_commands.py#L223
cmd_funcs, cmd_args = extract_commands_from_string(recognized)
executeCommands(robot, cmd_funcs, cmd_args) # 一定是一个参数


切割连接词 然后 接着 并且 并 之后，再，最后
    每个短语 提取 关键字，和余下的内容
    调用命令

https://github.com/rizal72/Cozmo-Voice-Commands/blob/master/cvc/voice_commands.py#L175

demo
    https://github.com/rizal72/Cozmo-Voice-Commands/blob/master/cvc/languages/en.json
    cozmo 往前走5秒  Cozmo drives forward for X seconds.
    Cozmo says X
    Cozmo dances.

http://cozmosdk.anki.com/docs/generated/cozmo.robot.html#cozmo.robot.Robot.drive_wheel_motors 
cozmo持续移动
人脸有关
    http://cozmosdk.anki.com/docs/generated/cozmo.robot.html#cozmo.robot.Robot.enable_facial_expression_estimation
表演
    http://cozmosdk.anki.com/docs/generated/cozmo.anim.html#cozmo.anim.Triggers.CodeLabCat
    使用 play_anim
    http://cozmosdk.anki.com/docs/generated/cozmo.anim.html#cozmo.anim.Triggers
    cozmo的行为

cozmo 前进50毫米，然后右转90度，最后表演一下学猫叫
'''

# 切割到单句
from codelab_adapter.core_extension import Extension

import re
import time

class SimpleNLU:
    separator_words = ["然后", "接着", "并且", "并", "之后", "再", "最后"]

    # actions = "" # 在Scratch中做，提取数字
    # demo : user_input -> "cozmo 前进50毫米，然后右转90度，最后表演一下学猫叫"

    def separate_sentences(self, user_input):
        sentences = re.split('|'.join(self.separator_words), user_input)
        return sentences

    def extract_float(self, string):
        matches = re.findall(r"[+-]?\d+\.?\d*", string)  # 整数或小数
        if matches:
            return matches[0]
        else:
            return "None"


class NLUExtension(Extension):

    NODE_ID = "eim/extension_simple_NLU"
    HELP_URL = "http://adapter.codelab.club/extension_guide/simple_NLU/"
    VERSION = "1.0"  # extension version
    DESCRIPTION = "simple NLU"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.simpleNLU = SimpleNLU()

    def run_python_code(self, code):
        # fork from python extension
        try:
            output = eval(code, {"__builtins__": None}, {
                "simpleNLU": self.simpleNLU,
            })
        except Exception as e:
            output = str(e)
        return output

    def extension_message_handle(self, topic, payload):
        self.logger.info(f'python code: {payload["content"]}')
        message_id = payload.get("message_id")
        python_code = payload["content"]
        output = self.run_python_code(python_code)
        payload["content"] = output
        message = {"payload": payload}  # 无论是否有message_id都返回
        self.publish(message)

    def run(self):
        "避免插件结束退出"
        while self._running:
            time.sleep(0.5)


export = NLUExtension