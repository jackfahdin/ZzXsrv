"""Original, deterministic OpenType/CFF test font; no external font assets.

The sole encoded glyph U+0041 is a 400 x 700 unit rectangle.  This fixture
deliberately needs no fontTools installation or downloaded fonts.
"""
import struct


def make_cff_font(family='FreeType Test Rectangle'):
    def pack(fmt, *values):
        return struct.pack('>' + fmt, *values)

    def index(items):
        offsets = [1]
        for item in items:
            offsets.append(offsets[-1] + len(item))
        return pack('HB', len(items), 1) + bytes(offsets) + b''.join(items)

    def number(value):
        return b'\x1c' + pack('h', value)

    names = index([b'FreeTypeTestRectangle'])
    # A fixed-width DICT integer makes the CharStrings offset independent of
    # its own value.  The predefined ISOAdobe charset supplies two glyph names.
    top = index([b'\x1d' + pack('I', 0) + b'\x11'])
    prefix = b'\x01\x00\x04\x04' + names
    offset = len(prefix) + len(top) + 4  # empty String and Global Subr INDEXes
    top = index([b'\x1d' + pack('I', offset) + b'\x11'])
    rectangle = (number(100) + number(0) + b'\x15' +
                 b''.join(number(v) for v in (400, 0, 0, 700, -400, 0)) +
                 b'\x05\x0e')
    cff = prefix + top + b'\0\0\0\0' + index([b'\x0e', rectangle])
    cmap4 = pack('7H', 4, 32, 0, 4, 4, 1, 0)
    cmap4 += pack('9H', 65, 65535, 0, 65, 65535, 65472, 1, 0, 0)
    name_strings = [(family, 1), ('Regular', 2),
                    (family + ' Regular', 4),
                    ('FreeTypeTestRectangle', 6)]
    records, strings = b'', b''
    for value, name_id in name_strings:
        encoded = value.encode('utf-16-be')
        records += pack('6H', 3, 1, 0x409, name_id, len(encoded), len(strings))
        strings += encoded
    head = pack('4I2H2Q4h3H2h', 0x10000, 0x10000, 0, 0x5F0F3CF5,
                3, 1000, 0, 0, 100, 0, 500, 700, 0, 8, 2, 0, 0)
    hhea = pack('I3hH11hH', 0x10000, 800, -200, 0, 600,
                100, 100, 500, 1, 0, 0, 0, 0, 0, 0, 0, 2)
    os2 = bytearray(78)
    struct.pack_into('>HhHHH', os2, 0, 0, 600, 400, 5, 0)
    struct.pack_into('>I', os2, 42, 1)  # Basic Latin Unicode range
    os2[58:62] = b'TEST'
    struct.pack_into('>HHHhhhHH', os2, 62, 0x40, 65, 65, 800, -200, 0, 800, 200)
    tables = {
        b'CFF ': cff, b'OS/2': bytes(os2), b'head': head, b'hhea': hhea,
        b'hmtx': pack('HhHh', 600, 0, 600, 100), b'maxp': pack('IH', 0x5000, 2),
        b'cmap': pack('HHHHI', 0, 1, 3, 1, 12) + cmap4,
        b'name': pack('3H', 0, len(name_strings), 6 + len(records)) + records + strings,
        b'post': pack('I', 0x30000) + bytes(28),
    }

    def checksum(data):
        padded = data + bytes((-len(data)) % 4)
        return sum(struct.unpack('>' + 'I' * (len(padded) // 4), padded)) & 0xffffffff

    count = len(tables)
    power = count.bit_length() - 1
    result = bytearray(b'OTTO' + pack('4H', count, 16 << power, power,
                                    count * 16 - (16 << power)))
    payload, head_offset = bytearray(), None
    for tag, data in sorted(tables.items()):
        position = 12 + count * 16 + len(payload)
        result += tag + pack('3I', checksum(data), position, len(data))
        if tag == b'head':
            head_offset = position
        payload += data + bytes((-len(data)) % 4)
    result += payload
    struct.pack_into('>I', result, head_offset + 8,
                     (0xB1B0AFBA - checksum(result)) & 0xffffffff)
    return bytes(result)
