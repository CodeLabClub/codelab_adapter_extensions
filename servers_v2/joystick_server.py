'''
pip3 install pygame
手柄是传感器，而不是执行器
'''
import pygame
from pygame.locals import *
from codelab_adapter_client import AdapterNode
import queue
import time
import os


class JoystickNode(AdapterNode):
    def __init__(self):
        super().__init__()
        self.EXTENSION_ID = "eim/joystick" # handle it 
        # self.q = queue.Queue()

    def extension_message_handle(self, topic, payload):
        pass

    def exit_message_handle(self, topic, payload):
        self.terminate()

    def run(self):
        try:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.init()
            pygame.joystick.init()
            joystick_count = pygame.joystick.get_count()
            joysticks = [
                pygame.joystick.Joystick(x)
                for x in range(pygame.joystick.get_count())
            ]
            print(f"joystick_count: {joystick_count}")
            print('joystick start')
        except pygame.error:
            self.pub_notification('joystick error', type="ERROR")
        '''
        todo scratch专门的extension
            两个手柄
        '''
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()

        while self._running:
            rate = 20
            time.sleep(1 / rate)
            for e in pygame.event.get():
                # todo 过来的事件不知道是哪个手柄吗
                if e.type in [
                        pygame.locals.JOYAXISMOTION,
                        pygame.locals.JOYHATMOTION, pygame.locals.JOYBUTTONDOWN
                ]:
                    joy = e.joy
                    joystick = joysticks[joy]
                    message = self.message_template()
                    message["payload"]["joy"] = joy
                    if e.type == pygame.locals.JOYAXISMOTION:
                        x, y = joystick.get_axis(0), joystick.get_axis(1)
                        print(f'joy: {joy} axis x: {x}  axis y: {y}')
                        message["payload"]["type"] = "JOYAXISMOTION"
                        message["payload"]["x"] = x
                        message["payload"]["y"] = y
                        message["payload"]["content"] = f'joy:{joy} axis x:{x} y:{y}' # 展示
                        self.publish(message)
                    elif e.type == pygame.locals.JOYHATMOTION:
                        x, y = joystick.get_hat(0)
                        print(f'joy: {joy} hat x: {x}  hat y: {y}')
                        message["payload"]["type"] = "JOYHATMOTION"
                        message["payload"]["x"] = x
                        message["payload"]["y"] = y
                        message["payload"]["content"] = f'joy:{joy} hat x:{x} y:{y}'
                        self.publish(message)
                    elif e.type == pygame.locals.JOYBUTTONDOWN:
                        print(f'joy: {joy} button:{e.button}')
                        message["payload"]["type"] = "JOYBUTTONDOWN"
                        message["payload"]["button"] = str(e.button)
                        message["payload"]["content"] = f'joy:{joy} button {e.button}'
                        # import IPython;IPython.embed()
                        self.publish(message)

if __name__ == "__main__":
    try:
        node = JoystickNode()
        node.receive_loop_as_thread()
        node.run()
    except KeyboardInterrupt:
        node.terminate()