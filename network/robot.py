#!/usr/bin/env python3
import logging
import socket
import struct
from typing import Tuple

from network.message import *
from . import PORT, MAGIC


MAGIC = b"%"

class Robot():
    def __init__(self, port: int):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("0.0.0.0", port))
        self.sock.listen(1)
        logging.info(f"Listening on port {port}")

        conn, laptop_addr = self.sock.accept()
        logging.info(f"Received connection from {laptop_addr}")
        self.conn = conn
        self.remote_addr = laptop_addr

    def receive_message(self) -> Message:
        magic = self.conn.recv(1)
        while magic != MAGIC:
            magic = self.conn.recv(1)
        msg_type = self.conn.recv(1)
        packed_len = self.conn.recv(4)
        msg_len = struct.unpack("I", packed_len)[0]
        logging.info(f"Received message of type {msg_type} and length {msg_len}")

        if msg_type == b'C':
            coords = self.conn.recv(msg_len)
            x, y = struct.unpack("dd", coords)
            logging.info(f"Received current position x: {x} y: {y}")
            return CurrentPosMessage(x, y)
        elif msg_type == b'G':
            coords = self.conn.recv(msg_len)
            x, y = struct.unpack("dd", coords)
            logging.info(f"Received goto position x: {x} y: {y}")
            return GotoPosMessage(x, y)
        elif msg_type == b'P':
            updown = self.conn.recv(msg_len)
            updown_str = "down" if updown == b'd' else "up"
            logging.info(f"Received pen up/down: {updown_str}")
            return PenUpdownMessage(updown == b'd')
        else:
            raise ValueError(f"Received unknown message type {msg_type}")

    def send_ok(self):
        message = OkMessage()
        self.conn.sendall(message.to_str())

    def send_error(self, error_msg: bytes):
        error_bytes = error_msg.encode("utf-8")
        message = ErrorMessage(error_bytes)
        self.conn.sendall(message.to_str())

def test_robot():
    logging.basicConfig(level=logging.INFO)
    robot = Robot(PORT)
    while True:
        msg = robot.receive_message()
        logging.info(f"Received: {msg.pretty_print()}")

        resp_type = input("OK or error? (K/E)").lower()[0:1]
        if resp_type not in ["k", "e"]:
            print("Invalid choice, defaulting to OK")
            resp_type = "k"

        if resp_type == "k":
            robot.send_ok()
        else:
            reason = input("Error message?")
            robot.send_error(reason)

if __name__ == "__main__":
    test_robot()
