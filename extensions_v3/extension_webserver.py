'''
ref: https://bottlepy.org/docs/dev/tutorial.html
'''

import time
import webbrowser

import bottle
from bottle import route, run, template, view

from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import threaded
from codelab_adapter_client.utils import get_adapter_home_path, get_local_ip

# html 文件所在目录
bottle.TEMPLATE_PATH = [
    get_adapter_home_path() / "extensions",  # 优先搜索 html 模版所在目录
    get_adapter_home_path() / "src",
]


@route('/hi/<name>')
def index(name="world"):
    html = '''
    <p>hello {{name}}</p>
    '''
    return template(html, name=name)


@route('/html/<name>')
@view('hello')  # html.tpl, 修改 ~/codelab_adapter/src/html.tpl 之后, 需要重新运行webserver插件
def hello_html(name="world"):
    return dict(name=name)

# 可以新增你自己的 route

class WebServerExtension(Extension):
    NODE_ID = "eim/extension_webserver"
    HELP_URL = "https://adapter.codelab.club/extension_guide/webserver/"
    DESCRIPTION = "运行一个简易网站"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.port = 18080

    @threaded
    def _run_webserver_as_thread(self):
        try:
            run(host='0.0.0.0', port=self.port)
        except OSError as e:
            self.logger.warning(str(e))

    def run(self):
        self._run_webserver_as_thread()
        # ip
        ip  = get_local_ip()
        if not ip:
            ip = "127.0.0.1"
        webbrowser.open(f'http://{ip}:{self.port}/hi/codelab') # 局域网
        while self._running:
            time.sleep(0.5)


export = WebServerExtension
