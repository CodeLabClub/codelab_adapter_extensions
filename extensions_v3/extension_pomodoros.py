'''
Pomodoro Technique
番茄工作法
'''
import time
from codelab_adapter.core_extension import Extension


class PomodoroExtension(Extension):
    HELP_URL = "https://adapter.codelab.club/extension_guide/eim/"  # Documentation page for the project
    WEIGHT = 1  # weight for sorting, default : 0
    VERSION = 1.0  # extension version
    DESCRIPTION = "启动一个番茄时钟"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.NODE_ID = "eim"  # default : eim

    def send_message(self):
        self.logger.info(f'send eim message')
        message = self.message_template(
        )  # use self.logger.debug to view the message structure
        message["payload"]["content"] = "Pomodoro"
        self.publish(message)

    def run(self):
        '''
        run as thread
        '''
        i = 0
        # 1 minute == 60 seconds
        pomodoro_seconds = 25 * 60
        while self._running:

            time.sleep(1)
            i += 1

            if i % pomodoro_seconds == 0:
                # 整除
                self.send_message()
                self.pub_notification(content="起身看看窗外风景", type="warning")


export = PomodoroExtension
