import socket
import struct
import os

class Socket(object):
    """
    socket class
    protocolized socket for communication between dispatchers <-> runners
    #TODO: implement basic encryption for communication?
    """
    def __init__(self, socket_name=None, socket_type=socket.AF_INET, timeout=None):
        self.name = socket_name
        self.type = socket_type
        self.timeout = timeout
        self.socket = socket.socket(self.type, socket.SOCK_STREAM)
        self.socket.settimeout(self.timeout)
        self.connection = None
        self.peer_address = None
        self.timeout = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def listen(self):
        self.socket.bind(self.name)
        self.socket.listen(1)
        self.name = self.socket.getsockname() # works both INET and UNIX, redundant for UNIX
        return self.name

    def accept(self):
        self.connection, self.peer_address = self.socket.accept()
        self.connection.settimeout(self.timeout)
        return self.connection, self.peer_address

    def connect(self, socket_name=None):
        if socket_name:
            self.name = socket_name
        self.peer_address = self.name
        self.connection = socket.socket(self.type, socket.SOCK_STREAM)
        self.connection.settimeout(self.timeout)
        self.connection.connect(self.name)


    #def send(self, message):
    #    bmsg = message.encode()
    #    self.connection.sendall(struct.pack('!I', len(bmsg)) + bmsg)

    def send(self, message):
        bmsg = message.encode()
        msg_with_length = struct.pack('!I', len(bmsg)) + bmsg
        total_sent = 0
        while total_sent < len(msg_with_length):
            sent = self.connection.send(msg_with_length[total_sent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            total_sent = total_sent + sent
        return total_sent

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
    def __init__(self, socket_name=None):
        if not socket_name: #either allow OS to choose, or use provided
            socket_name = (socket.gethostname(), 0)
        super().__init__(socket_name=socket_name, socket_type=socket.AF_INET)


class UNIXSocket(Socket):
    def __init__(self, socket_name):
        super().__init__(socket_name=socket_name, socket_type=socket.AF_UNIX)

    def close(self):
        super().close()
        if os.path.exists(self.name):
            os.unlink(self.name)
