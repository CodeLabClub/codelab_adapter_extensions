'''
fork from node_webserver_flask
'''
import time
import os
import sys
import webbrowser
from loguru import logger
from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import get_or_create_node_logger_dir, install_requirement, threaded, get_local_ip, send_simple_message
from flask import Flask
from flask import request

# log for debug
node_logger_dir = get_or_create_node_logger_dir()
debug_log = str(node_logger_dir / "debug.log")
logger.add(debug_log, rotation="1 MB", level="DEBUG")

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, 被选召的孩子!'


@app.route('/digimon')
def digimon():
    # queue to adapter
    name = request.args.get('name', default=None)
    # send
    send_simple_message(f'digimon {name}')
    # logger.debug
    digimon_info = {
        "microbit": {
            "name": "micro:bit",
            "img": "https://img",
        },
        "cozmo": {
            "name": "Cozmo",
            "description": "拥有惊人的灵活性，像微缩版的瓦力，性格阴晴不定，做游戏时喜欢耍小聪明",
            "img": "https://scratch3-files.just4fun.site/cozmo-gif.gif",
            "url": "https://adapter.codelab.club/extension_guide/cozmo/"
        },
        "alphamini": {},
        "codelab": {},
        "mushrooms":{},
    }

    return f'''
<link href="https://unpkg.com/tailwindcss@^2/dist/tailwind.min.css" rel="stylesheet">

<figure class="bg-gray-100 rounded-xl p-8">
  <img class="mx-auto" src="{digimon_info.get(name).get('img')}" alt="" width="384" height="512">
  <div class="pt-6 text-center space-y-4">
    <blockquote>
      <p class="text-lg font-semibold">
        {digimon_info.get(name).get('description')}
      </p>
    </blockquote>
    <figcaption class="font-medium">
      <div class="text-cyan-600">
         {digimon_info.get(name).get('name')}
      </div>
      <div class="text-gray-500">
        Anki
      </div>
    </figcaption>
  </div>
</figure>
'''


class DigimonNode(AdapterNode):
    NODE_ID = "eim/node_digimon"

    def __init__(self, **kwargs):
        self.port = 18081
        super().__init__(logger=logger, **kwargs)

    @threaded
    def _run_webserver_as_thread(self):
        try:
            app.run(host="0.0.0.0", port=self.port)  # todo 作为线程启动？
        except OSError as e:
            self.logger.warning(str(e))

    def run(self):
        ip = get_local_ip()  # 固定下来打印
        if not ip:
            ip = "127.0.0.1"
        self._run_webserver_as_thread()
        webbrowser.open(f'http://{ip}:{self.port}/')  # 局域网

        while self._running:
            time.sleep(0.1)

    def terminate(self, **kwargs):
        super().terminate(**kwargs)
        logger.info("terminate!")
        time.sleep(0.1)
        # 停止当前进程 pid
        os._exit(0)


def main(**kwargs):
    try:
        node = DigimonNode(**kwargs)
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        # node.logger.debug("KeyboardInterrupt") # work mac
        if node._running:
            node.terminate()  # Clean up before exiting.
    finally:
        node.terminate()


if __name__ == "__main__":
    main()