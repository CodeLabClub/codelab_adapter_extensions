'''
ref: https://bottlepy.org/docs/dev/tutorial.html

fork from https://github.com/CodeLabClub/codelab_adapter_extensions/blob/master/extensions_v3/extension_webserver.py
'''

import time
import webbrowser
import queue

import requests
import bottle
from bottle import route, run, template, view, request

from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import threaded, get_local_ip
from codelab_adapter_client.utils import get_adapter_home_path
# html 文件所在目录
PORT = 18081
message_queue = queue.Queue()

bottle.TEMPLATE_PATH = [
    get_adapter_home_path() / "extensions",  # 优先搜索 html 模版所在目录
    get_adapter_home_path() / "src",
]


@route('/hi/<name>')
def index(name="world"):
    ip = get_local_ip()
    html = '''
    <p>IP: {{ip}}</p>
    <p>在 iOS 快捷指令里创建以下捷径(
    )</p>
    <img width=400 src="https://adapter.codelab.club/img/IMG_0015.PNG"/>
    </br>
    <a target="_blank" href="https://adapter.codelab.club/extension_guide/siri/">文档</a>
    <!--<p>Siri point: http://{{ip}}:{{PORT}}/api/message/siri?message=1</p>-->
    '''
    return template(html, name=name, ip=ip, PORT=PORT)


@route('/api/message/siri', method='POST')
def eim_post():
    # http post http://192.168.31.148:18080/eim/post message=1, iphone 捷径
    # 中文 使用post
    json_dict = request.json  # .get("message")
    message = json_dict.get("message", None)
    if message:
        # print(message) # eim
        # print(f"message, {message}")
        message_queue.put(message)
        return "ok"


# one = request.GET.get('one', '').strip()
@route('/api/message/siri', method='GET')
def eim_get():
    message = request.GET.get('message', '').strip()
    if message:
        # 发送到独立频道
        message_queue.put(message)
        return "ok"


@route('/html/<name>')
@view('hello'
      )  # html.tpl, 修改 ~/codelab_adapter/src/html.tpl 之后, 需要重新运行webserver插件
def hello_html(name="world"):
    return dict(name=name)


# 可以新增你自己的 route


class WebServerExtension(Extension):
    NODE_ID = "eim/extension_Siri"
    HELP_URL = "https://adapter.codelab.club/extension_guide/siri/"
    DESCRIPTION = "Hey Siri"

    def __init__(self):
        super().__init__()
        self.port = PORT

    @threaded
    def _run_webserver_as_thread(self):
        try:
            run(host='0.0.0.0', port=self.port)
        except OSError as e:
            self.logger.warning(str(e))

    def run(self):
        self._run_webserver_as_thread()
        # ip
        ip = get_local_ip()
        if not ip:
            ip = "127.0.0.1"
        webbrowser.open(f'http://{ip}:{self.port}/hi/codelab')  # 局域网
        while self._running:
            if not message_queue.empty():
                http_message = message_queue.get()

                message = self.message_template()
                message["payload"]["content"] = http_message
                self.publish(message)
            time.sleep(1 / 10)


export = WebServerExtension
