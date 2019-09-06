'''
EIM: Everything Is Message
'''
import time
from codelab_adapter.core_extension import Extension


class EIMExtension(Extension):
    '''
    Everything Is Message
    '''

    def __init__(self):
        super().__init__()
        self.EXTENSION_ID = "eim"

    def extension_message_handle(self, topic, payload):
        self.logger.info(f'eim message:{payload}')
        self.publish({"payload": payload})

    def run(self):
        '''
        run 会被作为线程调用
        '''
        i = 0
        while self._running:
            message = self.message_template()
            message["payload"]["content"] = str(i)
            self.publish(message)
            time.sleep(1)
            i += 1
            '''
            if i%5 == 0:
                self.pub_notification(content=i)
            '''


export = EIMExtension

if __name__ == "__main__":
    EIMExtension().run()  #or start_as_thread()