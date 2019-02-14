from io import StringIO
import contextlib
import sys
# import subprocess
# import webbrowser
from codelab_adapter import settings
from codelab_adapter.core_extension import Extension

# 安全性原则: 打开这个插件前，提醒社区用户确认积木中没有危险的Python代码， 允许社区成员举报危险代码
# 在EIM中运行Python代码，通用

class KernelExtension(Extension):
    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)
        self.TOPIC = "eim/python"
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
                message  = self.read() # python code
                self.logger.debug(message)
                topic = message.get("topic")
                if topic == self.TOPIC:
                    python_code = message.get("payload")
                    self.logger.info("run python code:{}".format(python_code))
                    try:
                        with self.stdoutIO() as s:
                            # 'hello world'[::-1]
                            # import re; print(re.search('just4fun', 'blog.just4fun.site').span())
                            exec(python_code) # 注意安全问题, 但应当支持灵活的教学和创造。 赋予用户能力，但提醒他们别让锤子砸伤脚。
                        output = s.getvalue()
                    except Exception as e:
                        output = str(e)
                    message = {"topic": self.TOPIC, "payload": str(output).rstrip()}
                    self.publish(message)


export = KernelExtension
