from socket import *
server_port = 12000
server_socket = socket(AF_INET, SOCK_STREAM)
# server_socket.bind(('127.0.0.1', server_port))
server_socket.bind(('10.1.21.52', server_port))
server_socket.listen(1)
print('The server is ready to receive')
connection_socket, addr = server_socket.accept()
while True:
    message = connection_socket.recv(1024)
    print(f'Skt: {connection_socket}, addr: {addr}, msg: {message}')
    # CRITICAL FIX: If data is empty, the client closed the connection!
    if not message: 
        print(f"Client at {addr} disconnected cleanly.")
        break
    txt = message.decode()
    if txt.lower() == 'quit':
       connection_socket.send("Goodbye!".encode())
       print('Closing connection and quitting')
       connection_socket.close()
       break 
    reply = txt.upper().encode()
    connection_socket.send(reply)
#    connection_socket.close()