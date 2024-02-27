import socket
import struct
import os

class Socket(object):
    """
    socket class
    protocolized socket for communication between dispatchers <-> runners
    """
    def __init__(self, socket_name=None, socket_type=socket.AF_INET):
        self.name = socket_name
        self.type = socket_type
        self.socket = socket.socket(self.type, socket.SOCK_STREAM)
        self.connection = None
        self.peer_address = None

    def listen(self):
        self.socket.bind(self.name)
        self.socket.listen(1)
        self.name = self.socket.getsockname() # works both INET and UNIX, redundant for UNIX
        return self.name

    def accept(self):
        self.connection, self.peer_address = self.socket.accept()
        return self.connection, self.peer_address

    def connect(self, host_socket):
        self.peer_address = host_socket
        self.connection = socket.socket(self.type, socket.SOCK_STREAM)
        self.connection.connect(host_socket)

    def send(self, message):
        bmsg = message.encode()
        self.connection.sendall(struct.pack('!I', len(bmsg)) + bmsg)

    def recv(self):
        msglen = self.connection.recv(4)
        if not msglen:
            return None
        msglen = struct.unpack('!I', msglen)[0]
        return self.recvn(msglen).decode()

    def recvn(self, n):
        data = bytearray()
        while len(data) < n:
            packet = self.connection.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def close(self):
        if self.socket:
            self.socket.close()
        if self.connection:
            self.connection.close()

class INETSocket(Socket):
    def __init__(self):
        super().__init__(socket_name=(socket.gethostname(), 0), socket_type=socket.AF_INET)


class UNIXSocket(Socket):
    def __init__(self, socket_name):
        super().__init__(socket_name=socket_name, socket_type=socket.AF_UNIX)

    def close(self):
        super().close()
        if os.path.exists(self.name):
            os.unlink(self.name)
