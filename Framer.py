import json
import io
import typing_extensions
import socket


class Framer:
    data: list
    incoming: bytearray

    def __init__(self):
        self.HEAD = "HEAD"
        self.FOOT = "FOOT"
        self.incoming = bytearray()
        self.data = []

    def WriteData(self, buffer: bytes) -> bool:
        self.incoming.extend(buffer)
        temp_data = self.incoming.decode(encoding="utf-8", errors="strict")
        head = temp_data.find(self.HEAD)
        if head == -1:
            return False

        foot = temp_data.find(self.FOOT, head)
        if foot == -1:
            return False

        new_data = temp_data[head + len(self.HEAD) : foot]
        encoded_data = new_data.encode(encoding="utf-8", errors="strict")
        self.incoming = self.incoming[len(encoded_data): ]
        self.data.append(new_data)
        return True

    def FrameAvailable(self) -> bool:
        return len(self.data) > 0

    def GetFrame(self) -> dict:
        return self.data.pop(0)

    def Serialize(self, data: str) -> str:
        return self.HEAD + data + self.FOOT
