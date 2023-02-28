import sys
import time
import webbrowser
import requests
from io import StringIO
import contextlib
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import verify_token, open_path_in_system_file_manager
from codelab_adapter.config import settings

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
    VERSION = "1.2"  # extension version, support python function
    DESCRIPTION = "Python eval/exec(function)"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.PyHelper = PyHelper()
        self.error_prefix = "error: "

    @contextlib.contextmanager
    def stdoutIO(self, stdout=None):
        old = sys.stdout
        if stdout is None:
            stdout = StringIO()
        sys.stdout = stdout
        yield stdout
        sys.stdout = old

    def run_python_code_with_exec(self, code):
        # global
        try:
            with self.stdoutIO() as s:
                # 'hello world'[::-1]
                # import re; print(re.search('just4fun', 'blog.just4fun.site').span())
                # exec(object[, globals[, locals]])
                exec(code, globals())
            output = s.getvalue()
        except Exception as e:
            # todo error begin
            output = self.error_prefix + str(e)
        return output
        
    def run_python_code_with_function_eval(self, code):
        try:
            # eval(expression, globals=None, locals=None)
            output = eval(code, globals())
        except Exception as e:
            # todo error begin
            output = self.error_prefix + str(e)
        return output
    
    def run_python_code_old(self, code):
        try:
            # eval(expression, globals=None, locals=None)
            output = eval(code, {"__builtins__": None}, {
                "PyHelper": self.PyHelper,
                "requests": requests,
            })
        except Exception as e:
            output = self.error_prefix + str(e)
        return output

    # @verify_token
    def extension_message_handle(self, topic, payload):
        self.logger.info(f'python code: {payload["content"]}')
        content = payload["content"] # eval/exec
        
        if (len(payload["content"]) > 5) and (content[0:4] in ['exec', 'eval']):
            # cheak token
            if payload["token"] != settings.token:
                output = self.error_prefix + "token is invalid"
            else:
                run_with = content[0:4]
                python_code = content[5:]

                if run_with == 'eval':
                    output = self.run_python_code_with_function_eval(python_code)
                if run_with == 'exec':
                    # todo create function(from client) 4 space
                    # verify_token
                    output = self.run_python_code_with_exec(python_code)
        else:
            # old eval
            python_code = content
            output = self.run_python_code_old(python_code)
        try:
            output = str(output)  # 不要传递复杂结构
        except Exception as e:
            output = self.error_prefix + str(e)
        payload["content"] = output
        message = {"payload": payload}
        self.publish(message)

    def run(self):
        "避免插件结束退出"
        while self._running:
            time.sleep(0.5)


export = PythonKernelExtension
