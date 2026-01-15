import math
import struct
import time

import bluetooth


class PositionTransmitter:
    def __init__(self, target_address=None):
        self.sock = None
        self.target_address = target_address

    def find_receiver(self):
        print("Scanning for PositionReceiver service...")
        services = bluetooth.find_service(uuid="00001101-0000-1000-8000-00805F9B34FB")

        for svc in services:
            if "Uncle Mark" in svc.get("name", ""):
                return svc["host"], svc["port"]

        # Fallback: if target address known, use default RFCOMM port
        if self.target_address:
            return self.target_address, 1
        return None, None

    def connect(self):
        addr = 'DC:A6:32:96:44:49'
        port = 1

        print(f"Connecting to {addr} on port {port}...")
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.connect((addr, port))
        print("Connected!")

    def send_position(self, x: float, y: float):
        if self.sock:
            data = struct.pack("ff", x, y)
            self.sock.send(data)

    def close(self):
        if self.sock:
            self.sock.close()


# Example integration with your vision code
if __name__ == "__main__":
    tx = PositionTransmitter()
    # Or specify address directly: PositionTransmitter("XX:XX:XX:XX:XX:XX")
    tx.connect()

    try:
        t = 0.0
        while True:
            x = math.sin(t)
            y = math.cos(t)
            tx.send_position(x, y)

            t += 0.1
            time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        tx.close()
