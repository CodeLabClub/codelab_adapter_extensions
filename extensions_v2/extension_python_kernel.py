from io import StringIO
import contextlib
import sys
import time
import subprocess
import webbrowser
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import verify_token
from codelab_adapter.settings import TOKEN

# 安全性原则: 打开这个插件前，提醒社区用户确认积木中没有危险的Python代码， 允许社区成员举报危险代码
# 在EIM中运行Python代码，通用


class PyHelper:
    def open_url(self, url):
        webbrowser.open(url)

    def mac_open(self, path):
        open_cmd = "/usr/bin/open"  # which open
        subprocess.call(f"{open_cmd} {path}", shell=True)


class PythonKernelExtension(Extension):
    def __init__(self):
        super().__init__()
        self.EXTENSION_ID = "eim/python"
        self.PyHelper = PyHelper()

    @contextlib.contextmanager
    def stdoutIO(self, stdout=None):
        old = sys.stdout
        if stdout is None:
            stdout = StringIO()
        sys.stdout = stdout
        yield stdout
        sys.stdout = old

    @verify_token
    def extension_message_handle(self, topic, payload):
        '''
        所有可能运行代码的地方，都加上验证，确认payload中代码风险和token
        '''
        self.logger.info(f'python code: {payload["content"]}')
        message_id = payload.get("message_id")
        python_code = payload["content"]

        try:
            # 出于安全考虑, 放弃使用exec，如果需要，可以自行下载exec版本
            # eval(expression, globals=None, locals=None)
            # 如果只是调用(插件指责）可以使用json-rpc
            output = eval(python_code, {"__builtins__": None}, {
                "PyHelper": self.PyHelper,
            })
        except Exception as e:
            output = e
        payload["content"] = str(output)
        message = {"payload": payload}  # 无论是否有message_id都返回
        self.publish(message)

    def run(self):
        "服务于UI"
        while self._running:
            time.sleep(0.5)


export = PythonKernelExtension
