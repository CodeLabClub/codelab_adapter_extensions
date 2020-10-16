'''
ref: https://bottlepy.org/docs/dev/tutorial.html

fork from https://github.com/CodeLabClub/codelab_adapter_extensions/blob/master/extensions_v3/extension_webserver.py

'''

import time
import webbrowser
import requests

import bottle
from bottle import route, run, template, view, request

from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import threaded
from codelab_adapter_client.utils import get_adapter_home_path, get_local_ip
# html 文件所在目录
PORT = 18082

bottle.TEMPLATE_PATH = [
    get_adapter_home_path() / "extensions",  # 优先搜索 html 模版所在目录
    get_adapter_home_path() / "src",
]


@route('/hi/<name>')
def index(name="world"):
    ip = get_local_ip()
    html = '''
    <p>IP: {{ip}}</p>
    <p>EIM point: http://{{ip}}:{{PORT}}/api/message/eim?message=1</p>
    '''
    return template(html, name=name, ip=ip, PORT=PORT)


@route('/api/message/eim', method='POST')
def eim_post():
    # http post http://192.168.31.148:18080/eim/post message=1, iphone 捷径
    # 中文 使用post
    json_dict = request.json  # .get("message")
    message = json_dict.get("message", None)
    if message:
        # print(message) # eim
        requests.get(
            f"https://codelab-adapter.codelab.club:12358/api/message/eim?message={message}"
        )
        print(f"message, {message}")
        return "ok"


# one = request.GET.get('one', '').strip()
@route('/api/message/eim', method='GET')
def eim_get():
    message = request.GET.get('message', '').strip()
    if message:
        requests.get(
            f"https://codelab-adapter.codelab.club:12358/api/message/eim?message={message}"
        )
        print(f"message, {message}")
        return "ok"


@route('/html/<name>')
@view('hello'
      )  # html.tpl, 修改 ~/codelab_adapter/src/html.tpl 之后, 需要重新运行webserver插件
def hello_html(name="world"):
    return dict(name=name)


# 可以新增你自己的 route


class WebServerExtension(Extension):
    NODE_ID = "eim/extension_webserver"
    HELP_URL = "https://adapter.codelab.club/extension_guide/webserver/"
    DESCRIPTION = "http eim adapter"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
            time.sleep(0.5)


export = WebServerExtension
