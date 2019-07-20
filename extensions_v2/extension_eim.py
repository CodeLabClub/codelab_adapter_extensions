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
        print(topic, payload, type(payload))
        if type(payload) == str:
            self.logger.info(f'scratch eim message:{payload}')
            return
        elif type(payload) == dict:
            self.logger.info(f'eim message:{payload}')
            self.publish({"payload": payload})

    def run(self):
        '''
        run 会被作为线程调用
        '''
        i = 0
        while self._running:
            payload = {}
            payload["content"] = str(i)
            payload["extension_id"] = self.EXTENSION_ID
            message = {"payload": payload}  # topic可选
            self.publish(message)
            self.logger.debug(f'pub {message}')
            time.sleep(1)
            i += 1
            '''
            if i%5 == 0:
                self.pub_notification(content=i)
            '''


export = EIMExtension

if __name__ == "__main__":
    EIMExtension().run()  #or start_as_thread()