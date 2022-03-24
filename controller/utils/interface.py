import os

from utils.defines import *


class Mouse:
    def __init__(self, path) -> None:
        self.fd = os.open(path, os.O_RDWR)
        self.btns = [False, False, False]
        try:
            os.write(self.fd, b'\x00' * 5)
        except Exception as e:
            raise e

    def __del__(self):
        try:
            os.write(self.fd, b'\x00' * 5)
            os.close(self.fd)
        except Exception as e:
            pass

    def report(self, x=0, y=0, l=None, r=None, m=None):
        if l is not None:
            self.btns[0] = l
        if r is not None:
            self.btns[1] = r
        if m is not None:
            self.btns[2] = m
        btn_state = 1 if self.btns[0] else 0
        btn_state += 2 if self.btns[1] else 0
        btn_state += 4 if self.btns[2] else 0
        btn_state = (btn_state).to_bytes(1, byteorder='little', signed=False)
        left_move = (x).to_bytes(2, 'little', signed=True)
        right_move = (y).to_bytes(2, 'little', signed=True)
        os.write(self.fd, btn_state + left_move + right_move)  # wheel_move

    def move(self, x=0, y=0):
        self.report(x=x, y=y)

    def btn_press(self, btn):
        self.btns[btn] = True
        self.report(l=self.btns[0], r=self.btns[1], m=self.btns[2])

    def btn_release(self, btn):
        self.btns[btn] = False
        self.report(l=self.btns[0], r=self.btns[1], m=self.btns[2])

    def wheel_move(self, x=0):
        pass


class KeyBoard:
    def __init__(self, path):
        self.fd = os.open(path, os.O_RDWR)
        try:
            os.write(self.fd, b"\x00" * 8)
        except Exception as e:
            raise e
        self.special_key_state = {
            KEY_LEFT_CTRL: False,
            KEY_LEFT_SHIFT: False,
            KEY_LEFT_ALT: False,
            KEY_LEFT_GUI: False,
            KEY_RIGHT_CTRL: False,
            KEY_RIGHT_SHIFT: False,
            KEY_RIGHT_ALT: False,
            KEY_RIGHT_GUI: False,
        }
        self.special_key_order = [KEY_LEFT_CTRL, KEY_LEFT_SHIFT, KEY_LEFT_ALT,
                                  KEY_LEFT_GUI, KEY_RIGHT_CTRL, KEY_RIGHT_SHIFT, KEY_RIGHT_ALT, KEY_RIGHT_GUI]
        self.key_state = set()

    def __del__(self):
        try:
            os.write(self.fd, b"\x00" * 8)
            os.close(self.fd)
        except Exception as e:
            pass

    def report(self,):
        byte_1 = 0
        for i in range(8):
            if self.special_key_state[self.special_key_order[i]]:
                byte_1 += 1 << i
        write_bytes = (byte_1).to_bytes(1, byteorder='little', signed=False)
        write_bytes += b'\x00'  # 保留
        for down_key in self.key_state:
            write_bytes += down_key
        for i in range(6 - len(self.key_state)):
            write_bytes += b'\x00'
        # print(write_bytes)
        os.write(self.fd, write_bytes)

    def key_press(self, key):
        if key in self.special_key_state:
            self.special_key_state[key] = True
        else:
            if len(self.key_state) < 7:
                self.key_state.add(key)
            else:
                return
        self.report()

    def key_release(self, key):
        if key in self.special_key_state:
            self.special_key_state[key] = False
        else:
            if key in self.key_state:
                self.key_state.remove(key)
            else:
                return
        self.report()
