import time
import requests # 加到主要依赖里，可能已经被依赖
import json

from scratch3_adapter import settings
from scratch3_adapter.core_extension import Extension

class TulingExtension(Extension):
    def __init__(self):

        name = type(self).__name__ # class name
        super().__init__(name)
        self.init_bot()

    def init_bot(self):
        self.userId = 123
        self.apiKey = "d116ebafbaeb49a486a809ec306a6e82"
        self.apiUrl = "http://openapi.tuling123.com/openapi/api/v2"
        
    def run(self):
        # run 会被作为线程调用
        while self._running:
            message = self.read()
            data = message.get("data")
            if data:
                content =  {
                                "perception": {
                                    "inputText": {
                                        "text": data
                                    },
                                },
                                "userInfo": {
                                    "apiKey": self.apiKey,
                                    "userId": self.userId
                                }
                            }
                res = requests.post(url=self.apiUrl, data=json.dumps(content))
                r = res.json()
                message = {"topic": "eim"}
                message["message"] = r['results'][0]['values'][r['results'][0]['resultType']]
                self.publish(message)
                # from IPython import embed;embed()
                # self.logger.debug("message:%s",str(message))

export = TulingExtension
