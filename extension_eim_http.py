import time
import requests
from codelab_adapter import settings
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import  ui_error

class EimHttpExtension(Extension):
    def __init__(self):
        '''
        异步的http
        '''
        name = type(self).__name__  # class name
        super().__init__(name)

    def run(self):
        while self._running:
            message = self.read()
            data = message.get('data')
            topic = message.get("topic")
            if (topic == "eim") and data:
                # 返回json还是text
                # url = "http://github.com"
                try:
                    url = data
                    r = requests.get(url)
                    response = r.text
                except:
                    response = "something error"
                message = {"topic": "eim", "message": response}
                self.publish(message)
                    
                    


export = EimHttpExtension
