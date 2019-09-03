import struct
import warnings


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


devices = { 0: 'general',
            1: 'motors',
            2: 'marker',
            3: 'led',
            4: 'color',
            5: 'sound',
            12: 'bumpers',
            13: 'light',
            14: 'battery',
            17: 'touch',
            20: 'cliff' }
rdevices = dict([reversed(i) for i in devices.items()])

commands = {
    'versions':    ([0, 0], 'B'),
    'disconnect':  ([0, 6], ''),
    'motors':      ([1, 4], '>ii'),
    'drive':       ([1, 8], '>i'),
    'turn':        ([1, 12], '>i'),
    'setpen':      ([2, 0], 'B'),
    'say':         ([5, 4], 'B'*16),
}


def truncate(lst, max_size=16):
    return list(lst[:min(len(lst), max_size)])

def str_to_payload(s):
    return truncate(bytes(s, 'ascii')) + [0] * (16 - len(s))

def convert_int(x):
    return list(round(x).to_bytes(4, 'big', signed=True))


board_ids = {
    'main': 0xA5,
    'color': 0xC6
}


def crc8(data):
    """Calculate crc8 of data, as defined in the root BLE protocol.

    >>> crc8([1, 2, 3])
    72
    >>> crc8([0, 255, 3, 245])
    209
    """
    crc = 0
    for c in data:
        for i in range(7,-1,-1):
            x = 2 ** i
            bit = crc & 0x80
            if c & x: bit = not bit
            crc <<= 1
            if bit: crc ^= 0x07
            crc &= 0xFF

    return crc & 0xFF


def build_command(name, *args):
    pkt = commands[name][0] + [0]
    fmt = commands[name][1]
    pkt += list(struct.pack(fmt, *args))
    packet_length = 19 # bytes + crc
    pkt += [0] * (packet_length - len(pkt))
    pkt += [crc8(pkt)]
    return pkt


def parse_response(data):
    if data[-1] != crc8(data[:-1]):
        warnings.warn('Bad CRC in response: {}'.format(data), RuntimeWarning)

    cmd = ''
    for kv in commands.items():
        if kv[1][0] == data[:2]:
            cmd = kv[0]
            break
    
    return AttrDict({ 'device' : devices[data[0]],
                      'command': cmd,
                      'command_id': data[1],
                      'id': data[:3], # Since host and device counters are
                                      # separate and can collide, we need to
                                      # check the command too
                      'payload': data[3:-1],
    })
