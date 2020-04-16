'''
todo 使用 bottle
todo webhook
'''

import time, socket
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import threaded
import webbrowser
from bottle import route, run, template
# queue
import queue
q = queue.Queue()

@route('/webserver/<message>')
def index(message):
    html = '''
    ok!
    '''
    if message == "hello":
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        html = "\nok!<p>IP:" + s.getsockname()[0] + "</p>\n"
    q.put(message)
    return template(html, name=message)

class WebServerExtension(Extension):
    def __init__(self):
        super().__init__()
        self.NODE_ID = self.generate_node_id(__file__)
        self.HELP_URL = "http://adapter.codelab.club/extension_guide/webserver/"
        self.port = 8080

    @threaded
    def run_webserver_as_thread(self):
        run(host='0.0.0.0', port=self.port)

    def run(self):
        self.run_webserver_as_thread()
        time.sleep(0.5)
        webbrowser.open(f'http://127.0.0.1:{self.port}/webserver/hello')
        while self._running:
            message_web = q.get()
            message = self.message_template()
            message["payload"]["content"] = message_web
            self.publish(message)


export = WebServerExtension