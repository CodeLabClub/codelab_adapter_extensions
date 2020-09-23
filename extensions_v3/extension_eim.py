'''
EIM: Everything Is Message
'''
import time
from codelab_adapter.core_extension import Extension


class EIMExtension(Extension):
    '''
    Everything Is Message

    The main feature of the extension is sending a message(i) every second and log the message from the client into the log file.

    how to view Log: https://adapter.codelab.club/dev_guide/debug/#_2 
    
    It is recommended to think of the EIMExtension as a extension template, based on which to build any extension you want    
    '''

    NODE_ID = "eim"
    HELP_URL = "https://adapter.codelab.club/extension_guide/eim/"  # Documentation page for the project
    WEIGHT = 100  # weight for sorting, default : 0
    VERSION = "1.0"  # extension version
    DESCRIPTION = "Everything Is a Message"
    ICON_URL = ""
    REQUIRES_ADAPTER = "" # ">= 3.2.0"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def extension_message_handle(self, topic, payload):
        self.logger.info(f'eim message:{payload}')
        self.publish({"payload": payload})

    def run(self):
        '''
        run as thread
        '''
        i = 0
        while self._running:
            message = self.message_template(
            )  # use self.logger.debug to view the message structure
            message["payload"]["content"] = str(i)
            self.publish(message)
            time.sleep(1)
            i += 1
            '''
            if i%5 == 0:
                self.pub_notification(content=i)
            '''


export = EIMExtension