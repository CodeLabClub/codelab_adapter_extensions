'''
使用aiohttp
todo 使用bottle
''' 

import time
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import threaded
import webbrowser
from bottle import route, run, template

@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)

class WebServerExtension(Extension):
    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)
        self.port = 8080

    @threaded
    def run_webserver_as_thread(self):
        run(host='0.0.0.0', port=self.port)

    def run(self):
        self.run_webserver_as_thread()
        time.sleep(0.5)
        webbrowser.open(f'http://127.0.0.1:{self.port}/hello/bottle')
        while self._running:
            time.sleep(1)

export = WebServerExtension