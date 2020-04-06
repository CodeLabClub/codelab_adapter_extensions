import time
import socket
import sys
import queue


# from loguru import logger
# from codelab_adapter_client import AdapterNode
from codelab_adapter.core_extension import Extension


class RoboMasterNode(Extension):
    def __init__(self):
        super().__init__()
        self.EXTENSION_ID = "eim/RoboMaster"
        
        self.q = queue.Queue()

    def get_robot_ip(self):
        '''
        todo timeout
        '''
        ip_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 绑定 IP 广播端口
        ip_sock.bind(('0.0.0.0', 40926))
        # 等待接收数据
        ip_str = ip_sock.recvfrom(1024) # 阻塞式的
        # 输出数据
        host = ip_str[-1][0]
        return host

    # thread
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
        # 类似vector模式
        self.logger.info(f'the message payload from scratch: {payload}')
        self.q.put(payload)

    def run(self):
        command_socket = self.create_command_socket()
        # 默认建立连接 command
        connect_msg = "command"
        command_socket.send(connect_msg.encode('utf-8'))
        buf = command_socket.recv(1024) # timeout
        # todo 开启事件上报, 完成后开启一个新的socket线程，接收事件，控制bucket token
        self.logger.info(f"connect: {buf}")
        self.pub_notification("RoboMaster Connected!", type="SUCCESS")
        while self._running:
            # 等待用户输入控制指令
            # msg = input(">>> please input SDK cmd: ") # 默认连接
            # 等待来自Scratch的命令
            time.sleep(0.05)
            if not self.q.empty():
                payload = self.q.get()
                
                msg = payload["content"]
                # 当用户输入 Q 或 q 时，退出当前程序
                if msg.upper() == 'Q':
                    break

                # 发送控制命令给机器人
                command_socket.send(msg.encode('utf-8')) # noblock

                try:
                    # 等待机器人返回执行结果
                    buf = command_socket.recv(1024) # timeout
                    output = buf.decode('utf-8')
                    # print()
                    payload["content"] = str(output)
                    message = {"payload": payload}
                    self.publish(message)
                except socket.error as e:
                    self.logger.error(f"Error receiving :{e}", )
                    # sys.exit(1)
                if not len(buf):
                    break
        # end
        # 关闭端口连接
        command_socket.shutdown(socket.SHUT_WR)
        command_socket.close()
        self.logger.info("disconnect")

export = RoboMasterNode

if __name__ == "__main__":
    try:
        node = RoboMasterNode()
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        node.logger.info("exit...")
        time.sleep(1)
        node.terminate()  # Clean up before exiting.