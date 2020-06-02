import sys
import time
import subprocess
import webbrowser
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import verify_token, open_path_in_system_file_manager
from codelab_adapter.settings import TOKEN
'''
当前插件只允许运行表达式
如果你希望执行任意python代码，请使用: https://github.com/CodeLabClub/codelab_adapter_extensions/blob/master/extensions_v2/extension_python_kernel_exec.py，注意风险
安全性原则: 打开这个插件前，提醒社区用户确认积木中没有危险的Python代码， 允许社区成员举报危险代码
也可以在Scratch EIM插件中运行Python代码
'''


class PyHelper:
    def open_url(self, url):
        webbrowser.open(url)

    def open(self, path):
        open_path_in_system_file_manager(path)


class PythonKernelExtension(Extension):

    NODE_ID = "eim/extension_python"
    HELP_URL = "http://adapter.codelab.club/extension_guide/extension_python_kernel/"
    WEIGHT = 95
    VERSION = "1.0"  # extension version
    DESCRIPTION = "Python eval"

    def __init__(self):
        super().__init__()
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

    @verify_token
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
