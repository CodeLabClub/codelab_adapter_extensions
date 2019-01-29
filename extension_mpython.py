import time

from codelab_adapter import settings
from codelab_adapter.core_extension import Extension


import sys, socket, subprocess



class MpythonExtension(Extension):
    def __init__(self):
        name = type(self).__name__ # class name
        super().__init__(name)

    def run(self):
        # run 会被作为线程调用
        host = ''               
        port = 7788
        socksize = 1024

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        print("Server started on port: %s" %port)
        s.listen(5)
        print("Now listening...\n")
        conn, addr = s.accept()

        while self._running:
            message = self.read()
            self.logger.debug("message:%s",str(message))
            data = message.get("data")
            if data:
                shell = data
                conn.send(shell.encode('utf-8'))
                print('New connection from %s:%d' % (addr[0], addr[1]))
                data = conn.recv(socksize)
                # stdout,stderr = cmd.communicate()
                message = {"topic": "eim", "message": data.decode('utf-8')}
                self.publish(message)
                # 同步控制多个掌控板
            s.close()
export = MpythonExtension
