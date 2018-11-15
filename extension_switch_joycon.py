#!/usr/bin/env python
# encoding: utf-8

'''
EIM: Everything Is Message
'''
import time
import pygame
from pygame.locals import *
import os

from scratch3_adapter import settings
from scratch3_adapter.core_extension import Extension


try:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.init()
            pygame.joystick.init()
            joystick0 = pygame.joystick.Joystick(0)
            # 另一个手柄 pygame.joystick.Joystick(1)
            joystick0.init()
            print('joystick start')
except pygame.error:
            print('joystick error')

class EIMExtension(Extension):
    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)

    def run(self):
        '''
        run 会被作为线程调用
        当前插件功能:
            往scratch不断发送手柄信息
        '''


        while self._running:
                # message = {"topic": "eim", "message": "message"}
                # self.publish(message)
                # time.sleep(1)
            eventlist = pygame.event.get()
            for e in eventlist:
                if e.type == QUIT:
                    return

                if e.type == pygame.locals.JOYAXISMOTION:
                    x, y = joystick0.get_axis(0), joystick0.get_axis(1)
                    # print 'axis x:' + str(x) + ' axis y:' + str(y)
                    print('axis x:' + str(x) + ' axis y:' + str(y))
                elif e.type == pygame.locals.JOYHATMOTION:
                    x, y = joystick0.get_hat(0)
                    # print 'hat x:' + str(x) + ' hat y:' + str(y)
                    print('hat x:' + str(x) + ' hat y:' + str(y))
                elif e.type == pygame.locals.JOYBUTTONDOWN:
                    # print 'button:' + str(e.button)
                    print('button:' + str(e.button))
                    # 发往scratch
                    message = {"topic": "eim", "message": str(str(e.button))}
                    self.publish(message)

            time.sleep(0.1)


export = EIMExtension
