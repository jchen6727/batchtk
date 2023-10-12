"""
accept incoming connections from client
"""

import socket
import os

socket_path = '../my_socket.s'

try:
    os.unlink(socket_path)
except OSError:
    if os.path.exists(socket_path):
        raise

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

server.bind(socket_path)

server.listen(1) # can accept from one
print('listening for 1 connection...')
connection, client_address = server.accept()# actual blocking statement
print('Connection from', str(connection).split(", ")[0][-4:])

try:
    while True:
        data = connection.recv(1024)
        if not data:
            break
        print('Received data:', data.decode())
        connection.sendall("Hello from the server".encode())
finally:
    connection.close()
    os.unlink(socket_path)

