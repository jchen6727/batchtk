import socket
import struct
class Socket(object):
    """
    socket class
    protocolized socket for communication dispatchers <-> runners
    """
    def __init__(self, socketname=None, socket_type=socket.AF_UNIX, timeout=10):
        self.name = socketname
        self.type = socket_type
        self.socket = None
        #self.socket.bind(self.socketname)
        #self.socket.listen(1)
        self.connection = None
        self.peer_address = None

    def start(self):
        self.socket = socket.socket(self.type, socket.SOCK_STREAM)
        self.socket.bind(self.name)
        self.socket.listen(1)

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
        try:
            self.socket.close()
        except:
            pass
        try:
            self.connection.close()
        except:
            pass

class INETSocket(Socket):
    pass

class UNIXSocket(Socket):
    pass