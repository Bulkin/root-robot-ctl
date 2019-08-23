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
    'versions':    ([0, 0], 'byte'),
    'disconnect':  ([0, 6], None),
    'motors':      ([1, 4], 'int-pair'),
    'drive':       ([1, 8], 'int'),
    'turn':        ([1, 12], 'int'),
    'setpen':      ([2, 0], 'byte'),
    'say':         ([5, 4], 'str'),
}

def truncate(lst, max_size=16):
    return lst[:min(len(lst), max_size)]

def convert_int(x):
    return list(round(x).to_bytes(4, 'big', signed=True))

payload_types = {
    None: lambda x: [],
    'int': lambda x: convert_int(x),
    'int-pair': lambda x: convert_int(x[0]) + convert_int(x[1]),
    'byte': lambda x: [x],
    'str': lambda x: truncate(list(map(ord, x))),
}

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


def _pad(data):
    packet_length = 19 # bytes + crc
    data += [0x0] * (packet_length - len(data))
    data += [crc8(data)]
    return data


def build_command(name, payload=None):
    return _pad(commands[name][0] + [0]
                + payload_types[commands[name][1]](payload))


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
