import socket
import struct


class Connection:
    def __init__(self, connection:socket.socket):
        self.connection=connection

    def __repr__(self):
        return f"<Connection from {self.connection.getsockname()} to {self.connection.getpeername()}"
    
    def send_message(self, message:bytes) -> None:
        '''
        Sends a message through the socket.
        '''
        data_header=struct.pack('<i', len(message))
        self.connection.sendall(data_header+message)

    def receive_message(self)->str:
        try:
            data_header=self.connection.recv(4)
            if not data_header:
                return
            data_length = struct.unpack('<i', data_header)[0]
            data = self.connection.recv(data_length).decode()
            print(f'Received data: {data}\nData length: {data_length}')
            return (data_length,data)
            # response = f"Data received: {data}"
            # self.connection.sendall(response.encode())
        except ConnectionError:
            raise ConnectionError("Connection Lost!")
        
    @classmethod
    def connect(cls,host:str,port:int)->None:
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((host,port))
        return cls(s)

    def close(self)->None:
        self.connection.close()

    def __enter__(self)->Connection:
        return self
    
    def __exit__(self, exc_type, exc_value, traceback)->None:
        self.close()
    

    