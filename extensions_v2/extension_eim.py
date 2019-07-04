'''
EIM: Everything Is Message
'''
import time
import threading

from codelab_adapter.core_extension import Extension


class EIMExtension(Extension):
    '''
    插件功能: 往Scratch远远不断发送消息, 接收scratch过来的消息
    插件的topic统一为 from_adapter/extensions
    '''
    def __init__(self):
        super().__init__()
        # self.TOPIC = 'eim' # 默认 from_adapter/extension
        self.EXTENSION_ID = "eim" # extension_id

    def message_handle(self, topic, payload):
        '''
        handle the message from the scratch
        '''
        extension_id = payload.get('extension_id')
        if extension_id == self.EXTENSION_ID:
            self.logger.info(f'scratch eim message:{payload}')

    def run(self):
        '''
        run 会被作为线程调用
        '''
        i = 0
        while self._running:
            message = {"payload": str(i)} # 也允许有topic
            self.publish(message)
            self.logger.debug(f'pub {message}')
            time.sleep(1)
            i += 1
        
        self.clean_up()


export = EIMExtension

if __name__ == "__main__":
    EIMExtension().run()  #start_as_thread()
