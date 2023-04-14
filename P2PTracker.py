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

# logging setup 

logging.basicConfig(filename="logs.log", format="%(message)s", filemode="a")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# array with all threads' sockets
sockets = []

# dict with all connected clients and the un-checked chunks they have
check_list = {}

# dict with all connected clients and the checked chunks they have
chunk_list = {}

# dict with all verified hashes
chunk_dict = {}

def p2p_client_connection(socket, addr):
	# addr_key is client ip appended to client port
	addr_key = addr[0] + "," + str(addr[1])
	while(True):
		request = socket.recv(4096).decode()
		request = request.split(",")
		command = request[0]
		if command == "LOCAL_CHUNKS":
			addr_key = request[3] + "," + request[4]
			if addr_key not in check_list.keys():
				check_list[addr_key] = []
			if addr_key not in chunk_list.keys():
				chunk_list[addr_key] = []
			print()
			chunk_index, chunk_hash =  request[1], request[2]
			is_verified = False
			# checking if new chunk is verified and if so, move entries from check list to chunk list
			print("message ", request)
			for k, v in check_list.items():
				for chunk in v:
					if chunk == (chunk_index, chunk_hash):
						chunk_list[k].append(chunk)
						check_list[k].remove(chunk)
						is_verified = True
						break
			if is_verified or chunk_dict.get(chunk_index) == chunk_hash:
				chunk_list[addr_key].append((chunk_index, chunk_hash))
				chunk_dict[chunk_index] = chunk_hash
			else:
				check_list[addr_key].append((chunk_index, chunk_hash))

			print("check list, ", check_list)
			print("chunk list ", chunk_list)
			print()
		elif command == "WHERE_CHUNK":
			# get all clients that has target chunk
			target_chunk_index = request[1]
			print()
			print("request", request)
			target_chunk_hash = 0
			matching_clients = []
			response = []

			for k, v in chunk_list.items():
				for chunk in v:
					print("current chunk ", chunk)
					if target_chunk_index == chunk[0]:
						print("key", k)
						matching_clients.append(k)
						target_chunk_hash = chunk[1]
			
			print("matching clients ", matching_clients)
			if len(matching_clients) == 0:
				response = ("CHUNK_LOCATION_UNKNOWN", target_chunk_index)
				log = ("P2PTracker", "CHUNK_LOCATION_UNKNOWN", str(target_chunk_index))
				log = ",".join(log)
				logger.info(log)
			else:
				response = ["GET_CHUNK_FROM", target_chunk_index, target_chunk_hash]
				log = ["P2PTracker", "GET_CHUNK_FROM", str(target_chunk_index), target_chunk_hash]
				for client in matching_clients:
					response.append(client)
					log.append("localhost")
					log.append(str(client.split(",")[1]))
				log = ",".join(log)
				logger.info(log)
			print(response)
			response = ",".join(response)
			socket.send(response.encode())
			print()

while(True):
	connection_socket, addr = server_socket.accept()
	thread = threading.Thread(target=p2p_client_connection, args=(connection_socket, addr,))
	thread.start()
	sockets.append(connection_socket)
	print("sockets", sockets)
	


if __name__ == "__main__":
	pass