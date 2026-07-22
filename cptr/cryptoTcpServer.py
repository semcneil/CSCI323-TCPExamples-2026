# cryptoTcpServer.py
#
# This is the server side of the cryptography project 1 for CEC 460/CS 425.
#
# Seth McNeill
# 2025 April 07

# from socket import *
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend  # for loading keys
from cryptography.fernet import Fernet  # symmetric key encryption
from cryptography.exceptions import InvalidSignature
import base64  # for encoding the keys for transport and loading into Fernet
import pdb 
import os  # for checking file existence
import datetime  # for dates and times
import time

def main(connAddress, connPort):
  # create exchange key
  # Generate a private key for use in the exchange.
  # This should be renewed for every new exchange. 
  exchange_key = ec.generate_private_key(
      ec.SECP384R1()
  )
  exchange_public_key = exchange_key.public_key()
  exchange_public_str = exchange_public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
  ).decode('utf-8')
  # print(f"My exchange public key: \n{exchange_public_str}")

  server_port = connPort
  server_socket = socket(AF_INET, SOCK_STREAM)
  server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # to allow it to reuse the address and not get Errno 48 must be before bind
  server_socket.bind((connAddress, server_port))
  server_socket.listen(1)
  print('The server is ready to receive')
  connection_socket, addr = server_socket.accept()
  message = connection_socket.recv(1024)
  print(f'Skt: {connection_socket}, addr: {addr}, msg: {message}')
  msg_split = message.decode().split('\n')
  my_salt = msg_split[-1]
  client_key_str = '\n'.join(msg_split[:-1])
  print(f'client key: \n{client_key_str}\nsalt: {my_salt}')
  # load text into a key 
  client_public_key = serialization.load_pem_public_key(
      client_key_str.encode(),
      backend=default_backend()
  )
  print(client_public_key)

  # create symmetric key
  exchange_shared_key = exchange_key.exchange(ec.ECDH(), client_public_key)
  # Perform key derivation.
  exchange_derived_key = HKDF(
      algorithm=hashes.SHA256(),
      length=32,
      salt=my_salt.encode(),
      info=b'handshake data',
  ).derive(exchange_shared_key)
  print(f"Symmetric key:\n{exchange_derived_key}")

  reply = exchange_public_str.encode()
  connection_socket.send(reply)

  # wait for encrypted response
  print("waiting for encrypted message")
  enc_message = connection_socket.recv(1024)
  print(f"Received: \n{enc_message}")
  # decrypt response
  private_F_key = base64.urlsafe_b64encode(exchange_derived_key)
  private_F = Fernet(private_F_key)
  decrypted_msg = private_F.decrypt(enc_message).decode('utf-8')
  print(f"Decrypted message:\n{decrypted_msg}")
  d_msg_split = decrypted_msg.split('\n')
  rcv_msg = d_msg_split[0]
  rcv_sig64 = d_msg_split[1]
  rcv_key = '\n'.join(d_msg_split[2:])
  print(f"message: {rcv_msg}")
  print(f"sig: {rcv_sig64}")
  print(f"rcv_key:")
  print(rcv_key)
  my_sig = base64.urlsafe_b64decode(rcv_sig64)

  # verify response
  # load key
  signing_public_key = serialization.load_pem_public_key(
     rcv_key.encode('utf-8'),
     backend=default_backend()
  )
  # print(signing_public_key)
  # verify
  try:
     signing_public_key.verify(my_sig, rcv_msg.encode('utf-8'), ec.ECDSA(hashes.SHA256()))
     print("Valid signature")
     connection_socket.send(b'\x01')
  except InvalidSignature as e:
     print("Invalid signature")
     connection_socket.send(b'\x00')
  connection_socket.close()

  # send verification result
#    connection_socket.close()


if __name__ == "__main__":
  while(1):
    try:
      print("============================")
      main('127.0.0.1', 12460)
    #   main('172.30.115.175', 12460)
    except Exception as e:
      print(f"Failed with {e}")
      time.sleep(5)