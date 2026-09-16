from __future__ import annotations

import socket
import struct

from typing_extensions import Self  # type: ignore


class Connection:
    def __init__(self, connection: socket.socket):
        self.connection = connection

    def __repr__(self):
        return f"<Connection from {self.connection.getsockname()} to {self.connection.getpeername()}"

    def send(self, message: bytes) -> None:
        """
        Sends a message through the socket.
        """
        data_header = struct.pack("<i", len(message))
        self.connection.sendall(data_header + message)

    def receive(self) -> str:
        try:
            data_header = self.connection.recv(4)
            if not data_header:
                return
            if len(data_header) != 4:
                raise ConnectionError("Incomplete data header!")

            data_length = struct.unpack("<i", data_header)[0]
            # Does not decode data anymore, just receives and transmits.
            data = b""
            while len(data) < data_length:
                chunk = self.connection.recv(data_length - len(data))
                if chunk is None:
                    raise ConnectionError("Conncetion closed while receiving data!")
                data += chunk
            print(f"Received data, data length: {data_length}")
            return (data_length, data)
        except ConnectionError:
            raise ConnectionError("Connection Lost!")

    @classmethod
    def connect(cls, host: str, port: int) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        return cls(s)

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
