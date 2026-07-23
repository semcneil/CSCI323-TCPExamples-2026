from socket import *
# server_name = '127.0.0.1'
server_name = '10.1.65.255'
server_port = 12034
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((server_name, server_port))
while(1):
    message = input('Input lowercase sentence:')
    client_socket.send(message.encode())
    reply = client_socket.recv(1024)
    print('From Server: ', reply.decode())
    if "quit" in message.lower():
        print("Shutting down client")
        client_socket.close()
        break
#	client_socket.close()