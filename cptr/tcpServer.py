"""
tcpServer.py
====================================
This is an example of running a TCP server in Python. Note that the IP address in the
server_socket.bind command must be a valid address. Use 127.0.0.1 for initial testing
since all computers have this set as localhost.

| Author: Seth McNeill
| Date: 2026 September 28
"""

from socket import *
import argparse

def main(ipAddr='127.0.0.1', portNum=12000):
    server_port = portNum
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((ipAddr, server_port))
    # server_socket.bind(('10.1.21.52', server_port))
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
            connection_socket.send("Quitting!".encode())
            print('Closing connection and quitting')
            connection_socket.close()
            break 
        if txt.lower() == 'bye':
            connection_socket.send("Goodbye!".encode())
            print('Closing connection and restarting')
            connection_socket.close()
            connection_socket, addr = server_socket.accept()
            continue 
        reply = "From Dr. Seth: ".encode() + txt.upper().encode()
        connection_socket.send(reply)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple TCP server. Surround the IP address with double quotes, but leave the port as just an integer.")
    parser.add_argument("-a", "--ipaddr", default="127.0.0.1", help="The IP address the server runs on")
    parser.add_argument("-p", "--port", type=int, default=12000, help="The TCP port for the server to attach to")
    args = parser.parse_args()
    main(ipAddr=args.ipaddr, portNum=args.port)