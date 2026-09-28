"""
tcpClient.py
====================================
This is an example of running a TCP client in Python. Note that the IP address in the
server_socket.bind command must be the same one as is used in tcpServer.py.

| Author: Seth McNeill
| Date: 2026 September 28
"""

from socket import *
import argparse

def main(ipAddr='127.0.0.1', portNum=12000, name="bob"):
    server_name = ipAddr
    server_port = portNum
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_name, server_port))
    while(1):
        message = input('Input lowercase sentence: ')
        client_socket.send(f"{name} sent: ".encode() + message.encode())
        reply = client_socket.recv(1024)
        print('From Server: ', reply.decode())
        if "quit" in message.lower() or "bye" in message.lower():
            print("Shutting down client")
            client_socket.close()
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple TCP server. Surround the IP address with double quotes, but leave the port as just an integer.")
    parser.add_argument("-a", "--ipaddr", default="127.0.0.1", help="The IP address the server runs on")
    parser.add_argument("-p", "--port", type=int, default=12000, help="The TCP port for the server to attach to")
    parser.add_argument("-n", "--name", default="Bob", help="The name the server gives in the response")
    args = parser.parse_args()
    main(ipAddr=args.ipaddr, portNum=args.port, name=args.name)