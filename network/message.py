import struct
from . import MAGIC

class Message():
    def __init__(self, msg_type: bytes):
        self.msg_type = msg_type

        if msg_type == b'C':
            self.long_type = "current_pos"
        elif msg_type == b'G':
            self.long_type = "goto_pos"
        elif msg_type == b'P':
            self.long_type = "pen_updown"
        elif msg_type == b'K':
            self.long_type = "ok"
        elif msg_type == b'E':
            self.long_type = "error"
        else:
            raise ValueError(f"Unknown message type {msg_type}")

    """build_header creates a message header. The header consists of a magic
    byte, a byte indicating the message type, and the length of the message body.
    The possible message types are:
    * 'C' - Current position of the robot
    * 'G' - Position for the robot to go to
    * 'P' - Putting the pen up or down
    * 'K' - Response from robot: OK
    * 'E' - Response from robot: Error"""
    def build_header(self, length: int) -> bytes:
        return MAGIC + self.msg_type + struct.pack("I", length)

class CurrentPosMessage(Message):
    def __init__(self, x: float, y: float):
        super().__init__(b'C')
        self.x = x
        self.y = y

    def to_str(self) -> bytes:
        body = struct.pack("dd", self.x, self.y)
        return self.build_header(len(body)) + body

    def pretty_print(self) -> str:
        return f"Current pos is x: {self.x}, y: {self.y}"

class GotoPosMessage(Message):
    def __init__(self, x: float, y: float):
        super().__init__(b'G')
        self.x = x
        self.y = y

    def to_str(self) -> bytes:
        body = struct.pack("dd", self.x, self.y)
        return self.build_header(len(body)) + body

    def pretty_print(self) -> str:
        return f"Go to x: {self.x}, y: {self.y}"
        
class PenUpdownMessage(Message):
    def __init__(self, pen_down: bool):
        super().__init__(b'P')
        self.pendown = pen_down

    def to_str(self) -> bytes:
        body = b'd' if self.pendown else b'u'
        return self.build_header(len(body)) + body

    def pretty_print(self) -> str:
        dir = "down" if self.pendown else up
        return f"Put the pen {dir}"

class OkMessage(Message):
    def __init__(self):
        super().__init__(b'K')

    def to_str(self) -> bytes:
        return self.build_header(0)

    def pretty_print(self) -> str:
        return "Uncle Mark says OK!"

class ErrorMessage(Message):
    def __init__(self, reason: bytes):
        super().__init__(b'E')
        self.reason = reason

    def to_str(self) -> bytes:
        return self.build_header(len(self.reason)) + self.reason
    
    def pretty_print(self) -> str:
        return f"Uncle Mark is sad: {self.reason}"
