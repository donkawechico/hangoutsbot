import os, sys, asyncio, subprocess
from .cam import *

class Servo:
    _curpos = 0

    def __init__(self, servo_id=None, default=None, increment=None, min_pos=500, max_pos=2500):
        if max_pos is None:
            max_pos = 2500
        if min_pos is None:
            min_pos = 500
        if default is None:
            default = int((min_pos + max_pos) / 2)
        if servo_id is None:
            servo_id = 0
        if increment is None:
            increment = 100

        self._servo_id = servo_id
        self._default = default
        self._increment = increment
        self._min = min_pos
        self._max = max_pos

        self.reset()

        self._curpos = self._default

    def set_absolute_pos(self, amount=None):
        self.turn_to(amount)

    def set_default_pos(self):
        self._default = self._curpos

    def turn_counter_clockwise(self, amount=None):
        if amount is None:
            amount = self._increment
        print("Amount: {0}".format(amount))
        self.turn_increment(-amount)

    def turn_clockwise(self, amount=None):
        if amount is None:
            amount = self._increment

        self.turn_increment(amount)

    def turn_increment(self, amount=None):
        #self.validate(abs(amount))

        if amount > 0:
            symbol = "+"
        else:
            symbol = "-"

        with open('/dev/servoblaster', 'w') as f:
            f.write("{0}={1}{2}us\n".format(self._servo_id,symbol,abs(amount)))
            self._curpos = self._curpos + amount

    def turn_to(self, amount=None):
        #self.validate(abs(amount))

        with open('/dev/servoblaster', 'w') as f:
            f.write("{0}={1}us\n".format(self._servo_id,abs(amount)))
            self._curpos = amount

    def reset(self):
        self.turn_to(self._default)

    def validate(self, increment):
        if increment > self._max:
            raise ValueError("Position is invalid. Given: " + str(self._increment) + ", Min: " + str(self._min) + ", Max: " + str(self._max))


class PanTiltServo:
    def __init__(self, camera, leftright_increment=100, updown_increment=100):
        self._leftright = Servo(servo_id=0,default=1575,increment=leftright_increment)
        self._updown = Servo(servo_id=1,default=725,increment=updown_increment)
        self._camera = camera
        self.reset()

    def look_left(self,amount):
        self._leftright.turn_counter_clockwise(amount)

    def look_right(self,amount):
        self._leftright.turn_clockwise(amount)

    def look_down(self,amount):
        self._updown.turn_counter_clockwise(amount)

    def look_up(self,amount):
        self._updown.turn_clockwise(amount)

    def reset(self):
        self._leftright.reset()
        self._updown.reset()

    def save(self):
        self._leftright.set_default_pos()
        self._updown.set_default_pos()

    def moveto(self,lr_value,ud_value):
        self._leftright.set_absolute_pos(lr_value)
        self._updown.set_absolute_pos(ud_value)
