import zmq
import subprocess
import pathlib
import platform
import time
from codelab_adapter.core_extension import Extension
from codelab_adapter import settings
from codelab_adapter.utils import get_python3_path
'''
插件负责启停
使用adapter client
消息停止它
管理分布式插件
'''

python3_path = get_python3_path()


class VectorExtension(Extension):
    '''
    use to control VectorNode(server)
    '''
    def __init__(self):
        name = type(self).__name__
        super().__init__(name)
        self.EXTENSION_ID = "eim/vector/control" # default eim

    def operate_extensions(self, extension_id, command='stop'):

        payload = {
                "content": command,
                "extension_id": extension_id
        }
        self.publish_payload(payload, settings.EXTENSIONS_OPERATE_TOPIC)

    def run(self):
        codelab_adapter_server_dir = pathlib.Path.home(
        ) / "codelab_adapter" / "servers"
        script = "{}/vector_server.py".format(codelab_adapter_server_dir)

        cmd = [python3_path, script]
        vector_server = subprocess.Popen(cmd) # 发送ctrl c，但使用消息意味着可以分布式
        # todo 何时清理， 目前是在GUI exit里做
        settings.running_child_procs.append(vector_server)

        while self._running:
            time.sleep(0.1)
    
    def terminate(self):
        '''
        stop thread
        '''
        self.operate_extensions("eim/vector",'stop')
        self.clean_up()
        self.logger.info(f"{self} terminate!")


export = VectorExtension
