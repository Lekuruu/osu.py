from typing import List

import struct


class StreamOut:
    def __init__(self, endian="<"):
        self.endian = endian
        self.data = bytearray()
        self.pos = 0
        self.stack = []

    def push(self):
        self.stack.append(self.pos)

    def pop(self):
        self.pos = self.stack.pop()

    def get(self):
        return bytes(self.data)

    def size(self):
        return len(self.data)

    def tell(self):
        return self.pos

    def seek(self, pos):
        if pos > len(self.data):
            self.data += bytes(pos - len(self.data))
        self.pos = pos

    def skip(self, num):
        self.seek(self.pos + num)

    def align(self, num):
        self.skip((num - self.pos % num) % num)

    def available(self):
        return len(self.data) - self.pos

    def eof(self):
        return self.pos >= len(self.data)

    def write(self, data):
        self.data[self.pos : self.pos + len(data)] = data
        self.pos += len(data)

    def pad(self, num, char=b"\0"):
        self.write(char * num)

    def ascii(self, data):
        self.write(data.encode("ascii"))

    def u8(self, value):
        self.write(bytes([value]))

    def u16(self, value):
        self.write(struct.pack(self.endian + "H", value))

    def u32(self, value):
        self.write(struct.pack(self.endian + "I", value))

    def u64(self, value):
        self.write(struct.pack(self.endian + "Q", value))

    def s8(self, value):
        self.write(struct.pack("b", value))

    def s16(self, value):
        self.write(struct.pack(self.endian + "h", value))

    def s32(self, value):
        self.write(struct.pack(self.endian + "i", value))

    def s64(self, value):
        self.write(struct.pack(self.endian + "q", value))

    def u24(self, value):
        if self.endian == ">":
            self.u16(value >> 8)
            self.u8(value & 0xFF)
        else:
            self.u8(value & 0xFF)
            self.u16(value >> 8)

    def float(self, value):
        self.write(struct.pack(self.endian + "f", value))

    def double(self, value):
        self.write(struct.pack(self.endian + "d", value))

    def bool(self, value):
        self.u8(1 if value else 0)

    def char(self, value):
        self.u8(ord(value))

    def wchar(self, value):
        self.u16(ord(value))

    def intlist(self, numbers: List[int]):
        self.s16(len(numbers))
        [self.s32(num) for num in numbers]

    def uleb128(self, value: int):
        if value == 0:
            return b"\x00"

        ret = bytearray()

        while value != 0:
            ret.append(value & 0x7F)
            value >>= 7
            if value != 0:
                ret[-1] |= 0x80

        self.write(bytes(ret))

    def string(self, value: str):
        string = value.encode()
        length = len(string)  # + 1

        if not string:
            self.s8(0x00)
            return

        self.s8(0x0B)
        self.uleb128(length)
        self.write(string)


class StreamIn:
    def __init__(self, data: bytes, endian="<"):
        self.endian = endian
        self.data = data
        self.pos = 0
        self.stack = []

    def push(self):
        self.stack.append(self.pos)

    def pop(self):
        self.pos = self.stack.pop()

    def get(self):
        return self.data

    def size(self):
        return len(self.data)

    def tell(self):
        return self.pos

    def seek(self, pos):
        if pos > self.size():
            raise OverflowError("Buffer overflow")
        self.pos = pos

    def skip(self, num):
        self.seek(self.pos + num)

    def align(self, num):
        self.skip((num - self.pos % num) % num)

    def eof(self):
        return self.pos == len(self.data)

    def available(self):
        return len(self.data) - self.pos

    def peek(self, num):
        if self.available() < num:
            raise OverflowError("Buffer overflow")
        return self.data[self.pos : self.pos + num]

    def read(self, num):
        data = self.peek(num)
        self.skip(num)
        return data

    def readall(self):
        return self.read(self.available())

    def pad(self, num, char=b"\0"):
        if (self.read(num)) != char * num:
            raise ValueError("Incorrect padding")

    def ascii(self, num):
        return self.read(num).decode("ascii")

    def u8(self):
        return self.read(1)[0]

    def u16(self):
        return struct.unpack(self.endian + "H", self.read(2))[0]

    def u32(self):
        return struct.unpack(self.endian + "I", self.read(4))[0]

    def u64(self):
        return struct.unpack(self.endian + "Q", self.read(8))[0]

    def s8(self):
        return struct.unpack("b", self.read(1))[0]

    def s16(self):
        return struct.unpack(self.endian + "h", self.read(2))[0]

    def s32(self):
        return struct.unpack(self.endian + "i", self.read(4))[0]

    def s64(self):
        return struct.unpack(self.endian + "q", self.read(8))[0]

    def u24(self):
        if self.endian == ">":
            return (self.u16() << 8) | self.u8()
        return self.u8() | (self.u16() << 8)

    def float(self):
        return struct.unpack(self.endian + "f", self.read(4))[0]

    def double(self):
        return struct.unpack(self.endian + "d", self.read(8))[0]

    def bool(self):
        return bool(self.u8())

    def char(self):
        return chr(self.u8())

    def wchar(self):
        return chr(self.u16())

    def uleb128(self) -> int:
        length = shift = 0

        while True:
            byte = self.u8()

            length |= (byte & 0x7F) << shift
            if (byte & 0x80) == 0:
                break

            shift += 7

        return length

    def string(self) -> str:
        empty = self.s8() == 0x00

        if empty:
            return ""

        size = self.uleb128()
        return self.read(size).decode()

    def encoded_string(self) -> bytes:
        empty = self.s8() == 0x00

        if empty:
            return ""

        size = self.uleb128()
        return self.read(size)

    def intlist(self) -> List[int]:
        return [self.s32() for num in range(self.s16())]
