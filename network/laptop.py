#!/usr/bin/env python3
import logging
import socket
import struct

import math
import time

from .message import *
from . import PORT, MAGIC

# TODO: Use mutlicast DNS to auto-discover raspberry pi IP
RPI_ADDR = "172.20.10.5"

class Laptop():
    def __init__(self, ip: str):
        logging.info(f"Connecting to {ip}:{PORT}")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, PORT))
        logging.info("Connection successful")

    def send_current_pos(self, x: float, y: float):
        message = CurrentPosMessage(x, y)
        self.sock.sendall(message.to_str())

    def send_goto_pos(self, x: float, y: float):
        message = GotoPosMessage(x, y)
        self.sock.sendall(message.to_str())

    def send_pen_updown(self, pen_down: bool):
        message = PenUpdownMessage(pen_down)
        self.sock.sendall(message.to_str())

    def wait_for_bot(self) -> Message:
        logging.info("Waiting for response from bot...")
        magic = self.sock.recv(1)
        while magic != MAGIC:
            magic = self.sock.recv(1)
        msg_type = self.sock.recv(1)
        packed_len = self.sock.recv(4)
        msg_len = struct.unpack("I", packed_len)[0]
        body = self.sock.recv(msg_len)
        logging.info(f"Received message of type {msg_type}, len {msg_len}")

        msg = {}
        if msg_type == b'C':
            x, y = struct.unpack("dd", body)
            msg = CurrentPosMessage(x, y)
        elif msg_type == b'G':
            x, y = struct.unpack("dd", body)
            msg = GotoPosMessage(x, y)
        elif msg_type == b'P':
            if len(body) != 1:
                raise ValueError("Pen updown message too long")
            msg = PenUpdownMessage(body)
        elif msg_type == b'K':
            msg = OkMessage()
        elif msg_type == b'E':
            msg = ErrorMessage(body)
        else:
            raise ValueError(f"Invalid message type {msg_type}")

        return msg


def laptop_tester():
    logging.basicConfig(level=logging.INFO)
    laptop = Laptop(RPI_ADDR)
    while True:
        msg_type = input("Enter message type (CGP):")
        if msg_type not in ["C", "G", "P"]:
            print(f"Unknown message type {msg_type}")
            continue
        if msg_type == "C":
            x = float(input("Enter x:"))
            y = float(input("Enter y:"))
            laptop.send_current_pos(x, y)
            logging.info(f"Sent current pos: {x}, {y}")
        if msg_type == "G":
            x = float(input("Enter x:"))
            y = float(input("Enter y:"))
            laptop.send_goto_pos(x, y)
            logging.info(f"Sent goto pos: {x}, {y}")
        if msg_type == "P":
            updown = input("up or down? (u/d)").lower()[0:1]
            if updown not in ["u", "d"]:
                print("invalid up/down")
                continue
            laptop.send_pen_updown(updown == "d")
            logging.info(f"Sent pen up/down: {updown}")

        msg = laptop.wait_for_bot()
        logging.info(f"Received: {msg.pretty_print()}")
        
    logging.info("Test completed")

if __name__ == "__main__":
    laptop_tester()
