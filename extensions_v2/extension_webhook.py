'''
局域网通信
发送和接受http

消息

对应积木

Adapter Webhook
'''

import time
import socket
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import threaded
import webbrowser
from bottle import route, run, template
# queue
import queue
q = queue.Queue()

@route('/webhook/<message>')
def index(message):
    html = '''
    ok!
    '''
    if message == "hello":
        # hello page
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        html = f'''ok!
        <p>IP: {s.getsockname()[0]}</p>
        <p>Adapter Webhook url: http://{s.getsockname()[0]}/webhook/MESSAGE </p>
        '''
    q.put(message)
    return template(html, message=message)

class WebServerExtension(Extension):
    def __init__(self):
        super().__init__()
        self.port = 8080

    @threaded
    def run_webserver_as_thread(self):
        run(host='0.0.0.0', port=self.port)

    def run(self):
        self.run_webserver_as_thread()
        time.sleep(0.5)
        webbrowser.open(f'http://127.0.0.1:{self.port}/webhook/hello')
        while self._running:
            message_web = q.get()
            message = self.message_template()
            message["payload"]["content"] = message_web
            self.publish(message)


export = WebServerExtension