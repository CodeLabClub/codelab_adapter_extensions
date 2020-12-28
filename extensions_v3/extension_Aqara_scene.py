import hashlib
import subprocess
import sys
import time
import webbrowser

import requests

from codelab_adapter.core_extension import Extension
from codelab_adapter.settings import TOKEN
from codelab_adapter.utils import (open_path_in_system_file_manager,
                                   verify_token)


class PyHelper:    

    def set_id_key(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key

    def _get_headers(self, access_token):
        time_str = str(int(round(time.time() * 1000)))

        hl = hashlib.md5()
        hl.update(
            f"accesstoken={access_token}&appid={self.app_id}&time={time_str}&{self.app_key}"
            .encode('utf-8'))
        sign = hl.hexdigest()

        headers = {
            "Appid": self.app_id,
            "Accesstoken": access_token,
            "Time": time_str,
            "Content-Type": "application/json",
            "Sign": sign
        }
        return headers

    def run_scene(self, id, access_token):
        headers = self._get_headers(access_token)
        proxies = {
            "http": None,
            "https": None,
        }
        res = requests.post(
            "https://aiot-open-3rd.aqara.cn/3rd/v1.0/open/scene/run",
            proxies=proxies,
            headers=headers,
            json={"sceneId": id})
        return res.json()


class PythonKernelExtension(Extension):

    NODE_ID = "eim/extension_Aqara_scene"
    HELP_URL = "http://adapter.codelab.club/extension_guide/extension_Aqara_scene/"
    WEIGHT = 95
    VERSION = "1.0"  # extension version
    DESCRIPTION = "Aqara scene"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.PyHelper = PyHelper()

    def run_python_code(self, code):
        '''
        mode
            1  exec
            2  eval
            3  pass
        '''
        try:
            # 出于安全考虑, 放弃使用exec，如果需要，可以自行下载exec版本
            # eval(expression, globals=None, locals=None)
            # 如果只是调用(插件指责）可以使用json-rpc
            output = eval(code, {"__builtins__": None}, {
                "PyHelper": self.PyHelper,
            })
        except Exception as e:
            output = e
        return output

    def extension_message_handle(self, topic, payload):
        '''
        所有可能运行代码的地方，都加上验证，确认payload中代码风险和token
        '''
        self.logger.info(f'python code: {payload["content"]}')
        message_id = payload.get("message_id")
        python_code = payload["content"]
        output = self.run_python_code(python_code)
        payload["content"] = str(output)
        message = {"payload": payload}  # 无论是否有message_id都返回
        self.publish(message)

    def run(self):
        "避免插件结束退出"
        while self._running:
            time.sleep(0.5)


export = PythonKernelExtension
