from __future__ import annotations

import argparse
import sys
import threading

from card import Card
from connection import Connection
from listener import Listener


class Server:
    def __init__(self, host: str, port: int) -> Server:
        self.host = host
        self.port = port

    def start(self) -> None:
        with Listener(self.host, self.port) as listener:
            try:
                while True:
                    conn = listener.accept()
                    handle = Handler(conn)
                    handle.start()
            except KeyboardInterrupt:
                print("\nExiting server as per user request!")
                conn.close()


# We are inspired by the slides!
class Handler(threading.Thread):
    def __init__(self, connection: Connection):
        super().__init__()
        self.connection = connection

    def run(self):
        try:
            con = self.connection
            data_length, data = con.receive()
            if not data_length:
                return
            message_type = data[:1]
            payload = data[1:]
            if message_type == b"M":
                self.handle_message(payload)
            elif message_type == b"C":
                self.handle_card(payload)
            else:
                print(f"Unknown message type: {message_type!r}")
        except ConnectionError:
            print("Connection Lost!")

    def handle_message(self, data: bytes) -> None:
        message = data.decode()
        response = f"Message received: {message}"
        self.connection.send(response.encode())

    def handle_card(self, data: bytes) -> None:
        card = Card.deserialize(data)
        print(f"Card received: {card.name} from {card.creator}")

        response = f"Card received: {card.name} from {card.creator}"
        self.connection.send(response.encode())


def get_args():
    parser = argparse.ArgumentParser(description="Send data to server.")
    parser.add_argument("server_ip", type=str, help="the server's ip")
    parser.add_argument("server_port", type=int, help="the server's port")
    return parser.parse_args()


def main():
    """
    Implementation of a server.
    """
    args = get_args()
    s = Server(args.server_ip, args.server_port)
    s.start()


if __name__ == "__main__":
    sys.exit(main())
