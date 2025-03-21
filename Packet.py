import json

class Packet:
    def __init__(self, data_type: str, data: str):
        self.data_type = data_type
        self.data = data

    def __str__(self) -> str:
        return self.Serialize()

    def Serialize(self) -> str:
        return f"{self.data_type.upper()}: {self.data}\r\n"

def DeserializePacket(packet: str) -> Packet:
    data_type, data = packet.split(": ")
    return Packet(data_type, data)