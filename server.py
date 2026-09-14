import argparse
import socket
import struct
import sys

def run_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f'Server listening on {host}:{port}')
        while True:
            conn, addr = s.accept()
            with conn:
                print(f'Connected by {addr}')
                data_header = conn.recv(4)
                if not data_header:
                    break
                data_length = struct.unpack('<i', data_header)[0]
                data = conn.recv(data_length).decode()
                print(f'Received data: {data}')
                response = f"Data received: {data}"
                conn.sendall(response.encode())
                
def get_args():
    parser = argparse.ArgumentParser(description='Send data to server.')
    parser.add_argument('server_ip', type=str,
                        help='the server\'s ip')
    parser.add_argument('server_port', type=int,
                        help='the server\'s port')
    return parser.parse_args()


def main():
    '''
    Implementation of CLI and sending data to server.
    '''
    args = get_args()
    try:
        run_server(args.server_ip, args.server_port)
        print('Done.')
    except Exception as error:
        print(f'ERROR: {error}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
