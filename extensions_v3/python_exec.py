from io import StringIO
import contextlib
import sys
import time
# import subprocess
# import webbrowser
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import verify_token


class PythonKernelExtension(Extension):
    def __init__(self):
        super().__init__()
        self.NODE_ID = self.generate_node_id(__file__)

    @contextlib.contextmanager
    def stdoutIO(self, stdout=None):
        old = sys.stdout
        if stdout is None:
            stdout = StringIO()
        sys.stdout = stdout
        yield stdout
        sys.stdout = old

    def run_python_code(self, code):
        try:
            with self.stdoutIO() as s:
                # 'hello world'[::-1]
                # import re; print(re.search('just4fun', 'blog.just4fun.site').span())
                # exec(object[, globals[, locals]])
                exec(code)
            output = s.getvalue()
        except Exception as e:
            output = e
        return output

    @verify_token
    def extension_message_handle(self, topic, payload):
        '''
        所有可能运行代码的地方，都加上验证，确认payload中代码风险和token

        test: import webbrowser;webbrowser.open("https://www.codelab.club")
        
        '''
        self.logger.info(f'python code: {payload["content"]}')
        message_id = payload.get("message_id")
        python_code = payload["content"]
        output = self.run_python_code(python_code)
        payload["content"] = str(output)
        message = {"payload": payload}
        self.publish(message)

    def run(self):
        "避免插件结束退出"
        while self._running:
            time.sleep(0.5)


export = PythonKernelExtension
