'''
当前插件只允许运行表达式
如果你希望执行任意python代码，请使用: https://github.com/CodeLabClub/codelab_adapter_extensions/blob/master/extensions_v2/extension_python_kernel_exec.py，注意风险
安全性原则: 打开这个插件前，提醒社区用户确认积木中没有危险的Python代码， 允许社区成员举报危险代码
也可以在Scratch EIM插件中运行Python代码
'''

import time
import webbrowser
import requests
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import verify_token, open_path_in_system_file_manager


class PyHelper:
    def open_url(self, url, **kwargs):
        webbrowser.open(url, **kwargs)

    def open(self, path):
        open_path_in_system_file_manager(path)

    def bin2dec(self, string):
        return str(int(string, 2))


class PythonKernelExtension(Extension):

    NODE_ID = "eim/extension_python"
    HELP_URL = "http://adapter.codelab.club/extension_guide/extension_python_kernel/"
    WEIGHT = 95
    VERSION = "1.1"  # extension version
    DESCRIPTION = "Python eval"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.PyHelper = PyHelper()

    def run_python_code(self, code):
        try:
            # eval(expression, globals=None, locals=None)
            output = eval(code, {"__builtins__": None}, {
                "PyHelper": self.PyHelper,
                "requests": requests,
            })
        except Exception as e:
            output = str(e)
        return output

    # @verify_token
    def extension_message_handle(self, topic, payload):
        self.logger.info(f'python code: {payload["content"]}')
        python_code = payload["content"]
        output = self.run_python_code(python_code)
        try:
            output = str(output)  # 不要传递复杂结构
        except Exception as e:
            output = str(e)
        payload["content"] = output
        message = {"payload": payload}
        self.publish(message)

    def run(self):
        "避免插件结束退出"
        while self._running:
            time.sleep(0.5)


export = PythonKernelExtension
