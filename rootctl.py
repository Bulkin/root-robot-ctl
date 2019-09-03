import math
from queue import Queue
from collections import deque

import rootprotocol as rp
from rootbluetoothdevice import RootDeviceManager

class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, pt):
        return Point(self.x + pt.x, self.y + pt.y)

    def __repr__(self):
        return '<Point {} {}>'.format(self.x, self.y)
    
    def towards(self, pt):
        return math.atan2(pt.x - self.x, pt.y - self.y) % (2 * math.pi)

    def distance(self, pt):
        return math.sqrt((pt.x - self.x)**2 + (pt.y - self.y)**2)


class RootState:
    def __init__(self):
        self.pos = Point()
        self.angle = math.pi / 2
        self.pen = False
        self.eraser = False
  
    def forward(self, dist):
        self.pos += Point(dist * math.sin(self.angle),
                          dist * math.cos(self.angle))
        return rp.build_command('drive', dist)

    def backward(self, dist):
        return self.forward(-dist)
    
    def right(self, angle):
        """
        Turn right by \a angle degrees
        """
        self.angle += math.pi / 180 * angle
        self.angle %= 2 * math.pi
        return rp.build_command('turn', angle * 10)

    def left(self, angle):
        return self.right(-angle)

    def penup(self):
        self.pen = False
        self.eraser = False
        return rp.build_command('setpen', 0)

    def pendown(self):
        self.pen = True
        self.eraser = False
        return rp.build_command('setpen', 1)

    def say(self, phrase):
        return rp.build_command('say', *rp.str_to_payload(phrase))

    def goto(self, x, y):
        bearing = self.pos.towards(Point(x, y))
        distance = self.pos.distance(Point(x, y))

        angle = (bearing - self.angle) % (2 * math.pi)
        # turn left for forth quadrant, go backwards for second and third
        if angle > 1.5 * math.pi:
            angle -= 2 * math.pi
        elif angle > 0.5 * math.pi:
            angle -= math.pi
            distance *= -1

        print(self.pos, self.angle, bearing, distance, angle)
    
        self.pos = Point(x, y)
        
        return [ rp.build_command('turn', int(1800 / math.pi * angle)),
                 rp.build_command('drive', int(distance)),
                 rp.build_command('turn', int(-1800 / math.pi * angle)) ]

    def reset(self):
        angle = (self.angle - math.pi / 2)
        if abs(angle) > math.pi:
            angle = math.pi / 2 - self.angle
        return (goto(0, 0) +
                [rp.build_command('turn', 1800 / math.pi * angle)])
       
    def direct_drive(self, left, right):
        return rp.build_command('motors', left, right)


class RootDevice:
    def wrap_command(self, state_command):
        def wrapped(*args, **kwargs):
            commands = state_command(*args, **kwargs)
            if type(commands[0]) is not list:
                commands = [commands]
            for c in commands:
                id = self.robot.send_command(c)
                response = self.wait_for_response(id)

        return wrapped

    def __init__(self, bluetooth_adapter_name='hci0'):
        self.state = RootState()
        # Add command methods from RootState
        command_list = ['forward', 'backward',
                        'left', 'right',
                        'penup', 'pendown',
                        'say',
                        'goto', 'reset',
        ]
        for c in command_list:
            setattr(self, c, self.wrap_command(getattr(self.state, c)))

        self.robot = RootDeviceManager(adapter_name=bluetooth_adapter_name)
        self.result_queue = Queue()
        self.robot.connect(self.result_queue)
        response = self.result_queue.get()

    def __del__(self):
        self.disconnect()

    def disconnect(self):
        self.robot.disconnect()

    def wait_for_response(self, id):
        while True:
            response = self.result_queue.get()
            print(id, response)
            if response.id == id:
                return response

    def direct_drive(self, left, right):
        self.robot.send_command(self.state.direct_drive(left, right))


def test():
    root = RootDevice()

    root.say('hello world')
    root.pendown()

    for i in range(4):
        root.forward(100)
        root.right(90)

    root.disconnect()


if __name__ == '__main__':
    test()
