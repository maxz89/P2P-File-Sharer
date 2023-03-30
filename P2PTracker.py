from socket import *
import argparse
import threading
import sys
import hashlib
import time
import logging


#TODO: Implement P2PTracker

# initializing server socket
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(("127.0.0.1", 5100))
server_socket.listen(1)
print("Server started on port 5100. Accepting connections")
sys.stdout.flush()

while(True):
	connection_socket, addr = server_socket.accept()
	print(connection_socket, addr)


if __name__ == "__main__":
	pass