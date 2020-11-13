import time
import re
from loguru import logger
from codelab_adapter_client.utils import send_simple_message
from codelab_adapter.core_extension import Extension
from socketserver import BaseRequestHandler, TCPServer


class ScratchEchoHandler(BaseRequestHandler):

    def handle(self):
        print('Got connection from', self.client_address)
        while True:
            msg = self.request.recv(1024)
            print(f'msg:${msg}')
            if not msg:
                break
            else:
                logger.debug(f'socket request message: {msg}')
                # to adpaters
                message_decode = msg.decode()
                if "broadcast" in message_decode:
                    content = re.search(r'\"(.*?)\"', message_decode.split("broadcast")[-1]).groups()[0]
                    send_simple_message(content)
                    # if content == "exit":
                    #     self.server.shutdown()
                    #     self.server.server_close()
                    self.request.send(msg)
    

class SocketServerExtension(Extension):
    '''
    Socket Server
    最初用于实现与 Etoys 互操作: https://blog.just4fun.site/post/%E5%B0%91%E5%84%BF%E7%BC%96%E7%A8%8B/etoys-learning-note/
    
    socket client -> Scratch
    '''
    NODE_ID = "eim/extension_socket_server"
    HELP_URL = "https://adapter.codelab.club/extension_guide/socket_server/"  # Documentation page for the project
    VERSION = "1.0"  # extension version
    DESCRIPTION = "Socket Server"
    ICON_URL = ""
    REQUIRES_ADAPTER = "" # ">= 3.2.0"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.port = 42001
        self.address = '127.0.0.1'
        self.socket_server = TCPServer((self.address,self.port), ScratchEchoHandler)
        

    def extension_message_handle(self, topic, payload):
        pass

    def run(self):
        # 高频消息使用 osc
        self.socket_server.serve_forever()
    
    def terminate(self, **kwargs):
        self.logger.debug('terminate!')
        self.socket_server.shutdown() # 无法外部 shutdown
        self.socket_server.server_close()
        super().terminate(**kwargs)



export = SocketServerExtension