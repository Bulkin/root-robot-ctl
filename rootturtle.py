import turtle
from turtle import *
from rootctl import RootDevice

commands = ['forward', 'backward',
            'left', 'right', 'goto',
            'penup', 'pendown' ]

def _wrap_command(command_name):
    def wrapped(*args, **kwargs):
        getattr(_root, command_name)(*args, **kwargs)
        getattr(turtle, command_name)(*args, **kwargs)
    return wrapped


_root = RootDevice()
for c in commands:
    globals()[c] = _wrap_command(c)

pendown()
