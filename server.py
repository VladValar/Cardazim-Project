import argparse
import socket
import struct
import sys
import threading

class Server:
    def __init__(self,host:str,port:int)->Server:
        self.host=host
        self.port=port

    def start(self)->None:
        listener=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        listener.bind((self.host,self.port))
        listener.listen(1000)
        print(f'Server listening on {self.host}:{self.port}')
        try:
            while True:
                conn, addr = listener.accept()
                handle=Handler(conn)
                handle.start()
        except KeyboardInterrupt:
            print("\nExiting server as per user request!")
            conn.close()

                

#We are inspired by the slides!
class Handler(threading.Thread):
    def __init__(self, connection:socket.socket):
        super().__init__()
        self.connection=connection
        
    def run(self):
        try:
            con = self.connection
            data_header = con.recv(4)
            if not data_header:
                return
            data_length = struct.unpack('<i', data_header)[0]
            data = con.recv(data_length).decode()
            print(f'Received data: {data}\nData length: {data_length}')
            response = f"Data received: {data}"
            con.sendall(response.encode())
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
