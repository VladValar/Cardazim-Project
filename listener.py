import socket
from connection import Connection

class Listener:
    def __init__(self, host, port, backlog=1000):
        self.__host=host
        self.__port=port
        self.__backlog=backlog
        self.__server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __repr__(self)->str:
        return f"Listener(port={self.__port}, host=\"{self.__host}\", backlog={self.__backlog})"
    
    def start(self)->None:
        self.__server_socket.bind((self.__host,self.__port))
        self.__server_socket.listen(self.__backlog)
        print(f"Listening to {self.__backlog} connections on {self.__host}:{self.__port}")

    def close(self)->None:
        self.__server_socket.close()

    def accept(self)->Connection:
        try:
            conn,_=self.__server_socket.accept()
            return Connection(conn)
        except KeyboardInterrupt:
            print("\nQuitting listener as per user request!")
            self.close()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback)->None:
        self.close()