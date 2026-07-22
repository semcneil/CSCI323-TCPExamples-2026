# cryptoTcpClient.py
#
# This is the client side of the cryptography project 1 for CEC 460/CS 425.
#
# Seth McNeill
# 2025 April 07

from socket import *
from cryptography.hazmat.primitives import hashes # type: ignore
from cryptography.hazmat.primitives.asymmetric import ec  # type: ignore
from cryptography.hazmat.primitives.kdf.hkdf import HKDF # type: ignore
from cryptography.hazmat.primitives import serialization # type: ignore
from cryptography.hazmat.backends import default_backend  # for loading keys # type: ignore
from cryptography.fernet import Fernet  # symmetric key encryption # type: ignore
import base64  # for encoding the keys for transport and loading into Fernet 
import pdb 
import os  # for checking file existence
import datetime  # for dates and times


def createSigningKey():
  fname_privateKey = 'private.pem'
  signing_key = None
  if os.path.exists(fname_privateKey):
    # load signing private key from disk
    print(f"File '{fname_privateKey}' exists.")
    try:
      with open(fname_privateKey, "rb") as key_file:
        signing_key = serialization.load_pem_private_key(
          key_file.read(),
          password=None,
          backend=default_backend()
        )
      print("Successfully loaded signing key")
    except FileNotFoundError:
      print(f"Error: File not found at {fname_privateKey}")
    except Exception as e:
      print(f"An error occurred loading the signing key: {e}")
  else:
    # create new signing key and save to disk
    print(f"File '{fname_privateKey}' does not exist.")
    signing_key = ec.generate_private_key(
        ec.SECP384R1()  # Also called NIST P-384. https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ec/#elliptic-curves
    )
    signing_str = signing_key.private_bytes(
      encoding=serialization.Encoding.PEM,
      format=serialization.PrivateFormat.PKCS8,
      encryption_algorithm=serialization.NoEncryption()  # do not encrypt key for storage
    ).decode('utf-8')
    with open(fname_privateKey, 'w') as f:
      f.write(signing_str)
      f.close()
  return signing_key

def main(serverName, serverPort):
  signing_key = createSigningKey()
  my_salt = '01234567890123456789012345678932'
  # check/create signing key

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
  print(f"My exchange public key: \n{exchange_public_str}")
  # print(exchange_public_str)

  server_name = serverName
  server_port = serverPort
  client_socket = socket(AF_INET, SOCK_STREAM)
  try:
    client_socket.connect((server_name, server_port))
    message = exchange_public_str + "\n" + my_salt
    client_socket.send(message.encode())
    reply = client_socket.recv(1024)
    print('From Server: \n', reply.decode())
    # load text into a key 
    server_public_key = serialization.load_pem_public_key(
        reply,
        backend=default_backend()
    )
    print(server_public_key)
    # create symmetric key
    exchange_shared_key = exchange_key.exchange(ec.ECDH(), server_public_key)
    # Perform key derivation.
    exchange_derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=my_salt.encode(),
        info=b'handshake data',
    ).derive(exchange_shared_key)
    print(f"Symmetric key:\n{exchange_derived_key}")

    # create message to encrypt
    my_message = "Hello World from Dr. McNeill!"

    # sign message
    my_sig = signing_key.sign(my_message.encode('utf-8'), ec.ECDSA(hashes.SHA256()))
    my_sig64 = base64.urlsafe_b64encode(my_sig)
    print(f'My signature:\n{my_sig64}')
    signing_public_key = signing_key.public_key()
    signing_public_str = signing_public_key.public_bytes(
      encoding=serialization.Encoding.PEM,
      format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    full_msg = my_message + "\n" + my_sig64.decode('utf-8') + "\n" + signing_public_str

    # encrypt message
    private_F_key = base64.urlsafe_b64encode(exchange_derived_key)
    private_F = Fernet(private_F_key)
    private_token = private_F.encrypt(full_msg.encode('utf-8'))

    # send encrypted message to server
    client_socket.send(private_token)

    # check response to see if verified
    verified = client_socket.recv(1024)
    print(f'verified: {verified}')
    if verified == b'\x01':
      print("Message successfully verified")
    else:
      print("Message verification failed")

    #	client_socket.close()
  except ConnectionRefusedError as e:
    print(e)


if __name__ == "__main__":
  start_time = datetime.datetime.now()
  main('127.0.0.1', 12460)
#   main('173.236.244.178', 12460)

  end_time = datetime.datetime.now()
  print(f'Total time: {end_time-start_time} s')