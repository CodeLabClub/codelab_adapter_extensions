import time
import socket
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import threaded
import webbrowser
from bottle import route, run, template
import queue

q = queue.Queue()


@route('/word/<name>')
def index(name):
    html = '''
    ok!
    '''
    if name == "ip":
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        html = "\nok!<p>IP:" + s.getsockname()[0] + "</p>\n"
    q.put(name)
    return template(html, name=name)


# http://127.0.0.1:8080/word/motion1


class CalypsoExtension(Extension):

    NODE_ID = 'eim/extension_calypso'

    def __init__(self):
        super().__init__()
        self.
        self.HELP_URL = "http://adapter.codelab.club/extension_guide/Calypso/"
        self.port = 18081

    @threaded
    def run_webserver_as_thread(self, logger):
        try:
            run(host='0.0.0.0', port=self.port)
        except Exception as e:
            logger.error(str(e))

    def run(self):

        self.run_webserver_as_thread(self.logger)  # 无法捕获
        # get ip
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # cn -> 114.114.114.114
        ip = s.getsockname()[0]
        html = "\nok!<p>IP:" + ip + "</p>\n"
        # webbrowser.open(f'http://127.0.0.1:{self.port}/wand/hello')
        self.pub_notification(
            f'Calypso message address: http://{ip}:{self.port}/word/motion1')
        # time.sleep(0.5)
        while self._running:
            time.sleep(0.05)
            if not q.empty():
                message_web = q.get()
                message = self.message_template()
                message["payload"]["content"] = message_web
                self.publish(message)


export = CalypsoExtension