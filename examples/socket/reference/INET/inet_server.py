"""
accept incoming connections from client
"""

import socket

socket_path = ('192.168.1.157', 60000)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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


