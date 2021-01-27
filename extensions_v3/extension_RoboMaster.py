import time
import socket
import sys
import queue

from codelab_adapter.core_extension import Extension

class RoboMasterExtension(Extension):
    NODE_ID = "eim/extension_RoboMaster"
    HELP_URL = "http://adapter.codelab.club/extension_guide/RoboMaster/"
    DESCRIPTION = "开火！RoboMaster"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.q = queue.Queue()

    def get_robot_ip(self):
        '''
        todo: timeout
        '''
        ip_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_sock.bind(('0.0.0.0', 40926))
        # set timeout
        try:
            ip_sock.settimeout(3)
            # wait...
            ip_str = ip_sock.recvfrom(1024)  # block
            host = ip_str[-1][0]
            return host
        except Exception as e:
            self.pub_notification(str(e), type="ERROR")
            raise e

    def create_command_socket(self):
        command_port = 40923
        host = self.get_robot_ip()
        address = (host, int(command_port))
        command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger.info("Connecting...")
        command_socket.connect(address)
        self.logger.info("Connected!")
        return command_socket

    def extension_message_handle(self, topic, payload):
        # 采用与vector插件相同模式
        self.logger.info(f'the message payload from scratch: {payload}')
        self.q.put(payload)

    def run(self):
        command_socket = self.create_command_socket()
        # 默认建立连接
        connect_msg = "command;"
        command_socket.send(connect_msg.encode('utf-8'))
        buf = command_socket.recv(1024)  # todo: timeout
        # todo 开启事件上报, 默认开启，使用一个新的socket线程，接收事件。使用bucket token
        self.logger.info(f"connect: {buf}")
        self.pub_notification("RoboMasterEP 已连接", type="SUCCESS")
        while self._running:
            # wait for the command for the client(scratch/web app)
            time.sleep(0.05)
            if not self.q.empty():
                payload = self.q.get()
                msg = payload["content"]
                # send the command to the robot
                command_socket.send(msg.encode('utf-8'))  # todo: noblock

                try:
                    # wait for the reply
                    buf = command_socket.recv(1024)  # todo: timeout
                    output = buf.decode('utf-8')
                    payload["content"] = str(output)
                    message = {"payload": payload}
                    self.publish(message)
                except socket.error as e:
                    self.logger.error(f"Error receiving :{e}", )
                if not len(buf):
                    break
        # close the socket
        command_socket.shutdown(socket.SHUT_WR)
        command_socket.close()
        self.logger.info("disconnect")

export = RoboMasterExtension