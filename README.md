# Root robot control

Tools for controlling the [Root robot](https://root.irobot.com/).
Licensed under MIT, see LICENSE for details.

## Prerequisites

This project uses [`gatt-python`](https://github.com/getsenic/gatt-python) for
connecting to the robot via bluetooth. Typically `pip3 install --user gatt` is
enough.

## Example

```python
root = RootDevice()

root.say('hello world')
root.pendown()

# draw square
for i in range(4):
    root.forward(100)
    root.right(90)

root.disconnect()
```

## Turtle

The Root is basically a real world
[turtle](https://en.wikipedia.org/wiki/Turtle_graphics). There is a direct
mapping between `RootDevice` and python `turtle` commands, allowing us to draw
on the screen and whiteboard at the same time. For example:

```python
#!/usr/bin/env python3

from rootturtle import *

forward(100)
goto(0, 100)
right(90)
forward(100)
```

See `rootturtle.py` for details.


## Related

https://github.com/zlite/PyRoot : working proof of concept and layout drawing
with IMU.
