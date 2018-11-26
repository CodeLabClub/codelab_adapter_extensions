#!/usr/bin/env python
# encoding: utf-8
'''
EIM: Everything Is Message
'''
import sys
sys.path.append("/usr/local/lib/python3.6/site-packages")
import pygame
from pygame.locals import *
import os
import time

from scratch3_adapter import settings
from scratch3_adapter.core_extension import Extension

try:
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    pygame.joystick.init()
    joystick_count = pygame.joystick.get_count()
    joysticks = {}
    for i in range(joystick_count):
        joysticks[i] = pygame.joystick.Joystick(i)
        joysticks[i].init()
        print('joystick {} start'.format(i))
except pygame.error:
    print('joystick error')


class JoystickExtension(Extension):
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
                    print("axis: {}".format(str(e.dict)))
                elif e.type == pygame.locals.JOYHATMOTION:
                    # from IPython import embed;embed()
                    # e中携带了所有信息: e.dict
                    print("hat: {}".format(str(e.dict)))
                    # print('hat x:' + str(x) + ' hat y:' + str(y))
                elif e.type == pygame.locals.JOYBUTTONDOWN:
                    # 注意 两个手柄是一样的编码
                    print("button: {}".format(str(e.dict)))
                    # 只将button信息发往scratch
                    # todo: eim应该有处理json的能力，对于调试，直接say出来，看是什么即可
                    message = {"topic": "eim", "message": str(str(e.button))}
                    self.publish(message)

            time.sleep(0.1)


export = JoystickExtension
