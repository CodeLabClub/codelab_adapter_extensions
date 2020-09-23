'''
保存来自 Scratch stage 的 图像（base64格式）
    video
    stage
保存在~/codelab_adapter目录下
'''
import time
import os
import base64
import pathlib
import re

from loguru import logger
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import open_path_in_system_file_manager


def decode_image(src, name):
    """
    ref: https://blog.csdn.net/mouday/article/details/93489508
    解码图片
        eg:
            src="data:image/gif;base64,xxx" # 粘贴到在浏览器地址栏中可以直接显示
    :return: str 保存到本地的文件名
    """

    result = re.search("data:image/(?P<ext>.*?);base64,(?P<data>.*)", src,
                       re.DOTALL)
    if result:
        ext = result.groupdict().get("ext")
        data = result.groupdict().get("data")
    else:
        raise Exception("Do not parse!")

    img = base64.urlsafe_b64decode(data)

    filename = "{}.{}".format(name, ext)
    with open(filename, "wb") as f:
        f.write(img)
    # do something with the image...
    return filename


class StageExtension(Extension):
    NODE_ID = "eim/extension_stage"
    HELP_URL = "https://adapter.codelab.club/extension_guide/stage/"  # Documentation page for the project
    WEIGHT = 0  # weight for sorting, default : 0
    VERSION = "1.0"  # extension version
    DESCRIPTION = "将舞台区 图像/视频 发往 Adapter"
    ICON_URL = ""
    REQUIRES_ADAPTER = "" # ">= 3.2.0"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def extension_message_handle(self, topic, payload):
        # self.logger.info(f'the message payload from scratch: {payload}')
        content = payload.get("content", None)  # video积木可能为空
        if content and type(content) == str:
            # self.logger.debug(f"data -> {content}")
            codelab_adapter_dir = pathlib.Path.home() / "codelab_adapter"

            imgdata = content
            name = codelab_adapter_dir / 'stage'
            filename = decode_image(content, name)
            open_path_in_system_file_manager(filename)

            # reply
            payload["content"] = "ok"
            message = {"payload": payload}
            self.publish(message)

    def run(self):
        while self._running:
            time.sleep(0.5)


export = StageExtension