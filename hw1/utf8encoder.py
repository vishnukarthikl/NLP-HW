import math
import sys


def to_int(binary):
    return int(binary, 2)


class UTF8Char:
    def __init__(self, data):
        self.value = int(data, 2)
        self.binary = data

    def __str__(self):
        return self.binary

    def bytes(self):
        if len(self.binary) == 8:
            return [self.byte(1)]
        elif len(self.binary) == 16:
            return [self.byte(1), self.byte(2)]
        else:
            return [self.byte(1), self.byte(2), self.byte(3)]

    def byte(self, i):
        return chr(to_int(self.binary[(i - 1) * 8:i * 8]))


def convertToUTF8(character):
    if character.value < 128:
        return UTF8Char(''.join(character.binary[8:]))
    elif character.value < 2048:
        encoded = list("110xxxxx10xxxxxx")
    else:
        encoded = list("1110xxxx10xxxxxx10xxxxxx")

    character_in_binary = (['0'] * len(encoded)) + list(bin(character.value))[2:]
    for i in reversed(xrange(len(encoded))):
        if encoded[i] == 'x':
            encoded[i] = character_in_binary.pop()

    return UTF8Char(''.join(encoded))


class UTF16Char:
    def __init__(self, data):
        self.binary = self.convert_to_binary_string(data)
        self.calculate_value()

    def convert_to_binary_string(self, data):
        return ''.join(self.byte_to_string(data[0]) + self.byte_to_string(data[1]))

    def byte_to_string(self, byte):
        byte_string = []
        for i in xrange(8):
            byte_string.insert(0, str((ord(byte) >> i) & 1))
        return byte_string

    def calculate_value(self):
        self.value = 0
        for index, bit in enumerate(self.binary):
            self.value += int(int(bit) * math.pow(2, len(self.binary) - index - 1))


file_path = sys.argv[1]
chars_to_encode = []
with open(file_path, "rb") as f:
    data = f.read(2)
    while len(data) == 2:
        chars_to_encode.append(UTF16Char(data))
        data = f.read(2)

with open("utf8encoder_out.txt", "wb") as f:
    for char in map(convertToUTF8, chars_to_encode):
        for byte in char.bytes():
            f.write(byte)
