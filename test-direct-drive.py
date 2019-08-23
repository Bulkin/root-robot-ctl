#!/usr/bin/env python3

from inputs import get_gamepad
from rootctl import RootDevice

root = RootDevice()

right = 0
left = 0

while True:
    events = get_gamepad()
    for e in events:
        if e.code == 'ABS_Y':
            left = -int(e.state / 256 * 200 - 100)
        if e.code == 'ABS_RY':
            right = -int(e.state / 256 * 200 - 100)
        root.direct_drive(left, right)

