'''
使用aiohttp
todo 使用bottle
'''

import time
import socket
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import threaded
import webbrowser
from bottle import route, run, template
import queue

q = queue.Queue()

@route('/wand/<name>')
def index(name):
    html = '''
    ok!
    '''
    if name == "hello":
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        html = "\nok!<p>IP:" + s.getsockname()[0] + "</p>\n"
    q.put(name)
    return template(html, name=name)
# http://127.0.0.1:8080/wand/motion1

class WebServerExtension(Extension):
    def __init__(self):
        super().__init__()
        self.HELP_URL = "http://adapter.codelab.club/extension_guide/Kano_Wand/"
        self.port = 8080

    @threaded
    def run_webserver_as_thread(self):
        run(host='0.0.0.0', port=self.port)

    def run(self):
        self.run_webserver_as_thread()
        webbrowser.open(f'http://127.0.0.1:{self.port}/wand/hello')
        time.sleep(0.5)
        while self._running:
            message_web = q.get()
            message = self.message_template()
            message["payload"]["content"] = message_web
            self.publish(message)


export = WebServerExtension