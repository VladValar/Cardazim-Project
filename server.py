import argparse
import socket
import struct
import sys
import threading

from connection import Connection
from listener import Listener


class Server:
    def __init__(self, host:str, port:int)->Server:
        self.host=host
        self.port=port

    def start(self)->None:
        with Listener(self.host, self.port) as listener:
            try:
                while True:
                    conn = listener.accept()
                    handle=Handler(conn)
                    handle.start()
            except KeyboardInterrupt:
                conn.close()
                raise KeyboardInterrupt("\nExiting server as per user request!")

                

#We are inspired by the slides!
class Handler(threading.Thread):
    def __init__(self, connection:Connection):
        super().__init__()
        self.connection=connection
        
    def run(self):
        try:
            con = self.connection
            data_length, message = con.receive_message()
            if not data_length:
                return
            response = f"Message received: {message}"
            con.send_message(response.encode())
        except ConnectionError:
            print("Connection Lost!")


def get_args():
    parser = argparse.ArgumentParser(description='Send data to server.')
    parser.add_argument('server_ip', type=str,
                        help='the server\'s ip')
    parser.add_argument('server_port', type=int,
                        help='the server\'s port')
    return parser.parse_args()


def main():
    '''
    Implementation of a server.
    '''
    args = get_args()
    try:
        s = Server(args.server_ip, args.server_port)
        s.start()
    except Exception as error:
        print(f'ERROR: {error}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
