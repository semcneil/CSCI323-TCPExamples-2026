from socket import *
#server_name = '127.0.0.1'
server_name = '172.30.190.238'
server_port = 12000
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((server_name, server_port))
while(1):
	message = input('Input lowercase sentence:').encode()
	client_socket.send(message)
	reply = client_socket.recv(1024)
	print('From Server: ', reply.decode())
#	client_socket.close()