#!/usr/bin/env python3

# Example from https://docs.python.org/3.7/library/turtle.html

from rootturtle import *

color('red', 'yellow')
begin_fill()
while True:
    forward(200)
    left(160)
    if abs(pos()) < 1:
        break
end_fill()
done()
