# -*- coding: utf-8 -*-
# Time : 2019/2/7 12:40
# Author : hubozhi
import json
import socket
import threading
import time
from concurrent.futures import thread
from math import *
from queue import Queue
from sys import exit

import pygame
from pygame.locals import *
from pygame.math import *

from utils.defines import *


class gpioController:
    def __init__(self) -> None:
        self.wasd = {
            KEY_W: False,
            KEY_A: False,
            KEY_S: False,
            KEY_D: False,
        }
        self.wheelPingMap = ["wheel_pin_0","wheel_pin_1", "wheel_pin_2", "wheel_pin_3",
                             "wheel_pin_4", "wheel_pin_5", "wheel_pin_6", "wheel_pin_7", "wheel_pin_8"]
        '''
        6   7   8
        3   4   5
        0   1   2
        '''
        self.wheelNow = self.wheelPingMap[4]
        self.key_map_wasd = [KEY_W, KEY_A, KEY_S, KEY_D]
        self.key_map_normal = {
            MOUSE_BTN_LEFT: "pin_10",
            KEY_1: "pin_11",
            KEY_2: "pin_12",
            KEY_3: "pin_13",
        }
        self.wheelDown = False

        self.running = True
        self.eventqueue = Queue()
        threading.Thread(target=self.mainLoop).start()

    def stop(self):
        self.running = False

    def setBtn(self, pin, connect):
        print(f"set {pin} to {connect}")

    def onWASD(self, keycode: bytes, down: bool):
        self.wasd[keycode] = down
        mapVal = 4
        mapVal += -1 if self.wasd[KEY_A] else 0
        mapVal += 1 if self.wasd[KEY_D] else 0
        mapVal += -3 if self.wasd[KEY_S] else 0
        mapVal += 3 if self.wasd[KEY_W] else 0
        if mapVal == 4:#如果目标值为4 即中心
            self.setBtn(self.wheelNow, False)#释放当前按钮
            self.wheelNow = self.wheelPingMap[4]#设置当前为中心
            self.wheelDown = False#wheel状态为抬起
        else:
            if self.wheelDown == False:#如果从抬起到按下
                self.setBtn(self.wheelPingMap[4], True)
                time.sleep(1 / 1)
                self.setBtn(self.wheelPingMap[4], False)
                self.setBtn(self.wheelPingMap[mapVal],True)
                self.wheelNow = self.wheelPingMap[mapVal]
                self.wheelDown = True
            else:#从一个方向到另一个方向
                self.setBtn(self.wheelNow, False)
                # time.sleep(1 / 1)
                self.setBtn(self.wheelPingMap[mapVal], True)
                self.wheelNow = self.wheelPingMap[mapVal]


    def mainLoop(self):
        while self.running:
            keycode,down = self.eventqueue.get()
            self.handelKeyEvent(keycode, down)    

    def handelKeyEvent(self, keycode: bytes, down: bool):
        if keycode in self.key_map_wasd:
            self.onWASD(keycode, down)
        elif keycode in self.key_map_normal:
            pin = self.key_map_normal[keycode]
            self.setBtn(pin, down)

    def putEvent(self, keycode: bytes, down: bool):
        print(f"put {keycode} {down}")
        self.eventqueue.put((keycode, down))





class sender:
    def __init__(self, ip, port) -> None:
        self.target = (ip, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data):
        self.socket.sendto(data, self.target)

    def __del__(self):
        self.socket.sendto(b'stop', self.target)
        self.socket.close()


lasttime = 0
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((320, 240), 0, 32)
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    toPi = sender("192.168.1.180", 8848)

    simulategpio = gpioController()


    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                simulategpio.stop()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    simulategpio.stop()
                    exit()
                data = json.dumps({
                    "type": "key",
                    "data": [event.scancode, True]
                })
                simulategpio.putEvent(event.scancode.to_bytes(1, byteorder="big", signed=False), True)
            elif event.type == KEYUP:
                # print(event.scancode)
                data = json.dumps({
                    "type": "key",
                    "data": [event.scancode, False]
                })
                simulategpio.putEvent(event.scancode.to_bytes(1, byteorder="big", signed=False), False)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                print(f"{event.button} down")
            elif event.type == pygame.MOUSEBUTTONUP:
                print(f"{event.button} up")
            elif event.type == pygame.MOUSEMOTION:
                rel = pygame.mouse.get_rel()
                rate = time.time() - lasttime
                lasttime = time.time()
                mouserel = f"x:{rel[0]}, y:{rel[1]}   rate:{int(1/ (rate if rate != 0 else 1)   )}"
                data = json.dumps({
                    "type": "mouse_move",
                    "data": rel
                })

                toPi.send(data.encode("utf-8"))
                # print()
            elif event.type == pygame.MOUSEWHEEL:
                print(event.y)
