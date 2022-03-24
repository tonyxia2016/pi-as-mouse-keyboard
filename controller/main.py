import json
import math
import os
import random
import socket
import time

from utils.defines import *
from utils.interface import *

# def resetPos():
#     vm.report(l=False)
#     vm.report(x=3000,y=3000)
#     vm.report(x=3000,y=3000)
#     time.sleep(0.01)
#     vm.report(x=-2200,y=-1700)
#     vm.report(l=True)


kb = KeyBoard(r'/dev/hidg0')
mouse = Mouse(r'/dev/hidg1')


def makeCircle(r):
    points = []
    for i in range(r):
        x = r * math.cos(i * 2 * math.pi / r)
        y = r * math.sin(i * 2 * math.pi / r)
        points.append((int(x), int(y)))
    offsets = []
    for i in range(len(points)-1):
        x = points[i+1][0] - points[i][0]
        y = points[i+1][1] - points[i][1]
        offsets.append((x,y))
    return offsets

pt = makeCircle(500)


# while True:
mouse.btn_press(MOUSE_BTN_LEFT)
for (x,y) in pt:
    mouse.report(x=x,y=y)
    time.sleep(0.001)
mouse.btn_release(MOUSE_BTN_LEFT)



    # time.sleep(0.5)

    # for i in range(3):
    #     mouse.move(3000,3000)

    # time.sleep(0.01)
    # mouse.move(-2200,-1700)



