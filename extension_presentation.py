from io import StringIO
import contextlib
import sys
import subprocess
import webbrowser
from codelab_adapter import settings
from codelab_adapter.core_extension import Extension

class PresentationExtension(Extension):
    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)

    @contextlib.contextmanager
    def stdoutIO(self, stdout=None):
        old = sys.stdout
        if stdout is None:
            stdout = StringIO()
        sys.stdout = stdout
        yield stdout
        sys.stdout = old

    def run(self):
        while self._running:
            if settings.DEBUG:
                message  = self.read()
                self.logger.info(message)
                python_code = message.get("payload")
                try:
                    with self.stdoutIO() as s:
                        # 不用rpc, 使用dynamicland的架构原则: 保持单一入口, message is everything (everything is message)
                        exec(python_code)
                    output = s.getvalue()
                except Exception as e:
                    output = str(e)
                message = {"topic": "eim", "payload": str(output)}
                self.publish(message)


export = PresentationExtension