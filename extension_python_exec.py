from io import StringIO
import contextlib
import sys
from scratch3_adapter import settings
from scratch3_adapter.core_extension import Extension

class ExecExtension(Extension):
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
                message  = self.read() # python code
                self.logger.info(message)
                python_code = message.get('data')
                try:
                    with self.stdoutIO() as s:
                        # 'hello world'[::-1]
                        # import re; print(re.search('just4fun', 'blog.just4fun.site').span())
                        exec(python_code)
                    output = s.getvalue()
                except Exception as e:
                    output = str(e)
                message = {"topic": "eim", "message": str(output)}
                self.publish(message)


export = ExecExtension