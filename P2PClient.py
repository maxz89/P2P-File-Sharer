from socket import *
import argparse
import threading
import sys
import hashlib
import time
import logging
import random
import os
import logging

# parsing command line arguments
# p2pclient.py -folder <my-folder-full-path> -transfer_port <transfer-port-num> -name <entity-name>

parser = argparse.ArgumentParser()
parser.add_argument('-folder')
parser.add_argument('-transfer_port')
parser.add_argument('-name')
args = parser.parse_args()
# path to folder with chunk data, port for connecting with other clients, name of client for logging
folder, client_port, client_name, client_ip = args.folder, args.transfer_port, args.name, "127.0.0.1"

# logging setup 

logging.basicConfig(filename="logs.log", format="%(message)s", filemode="a")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# parsing local_chunks.txt and extracting lines
# var chunks is a list of each line in txt as strings
with open(folder+'/local_chunks.txt') as file:
	raw_chunks = file.readlines()

# number of total chunks in folder
total_num_chunks = int(raw_chunks[-1][0])

# the chunks in the client's folder currently
chunk_set = set()

# chunks currently downloading
temp_set = set()

# takes in file path and returns hash of file
def hash_file(file_path):
    hash = hashlib.sha1()
    with open(file_path,'rb') as file:
        # loop till the end of the file
        chunk = 0
        while chunk != b'':
            # read only 1024 bytes at a time
            chunk = file.read(1024)
            hash.update(chunk)

    return hash.hexdigest()


parsed_chunks = []
for i in range(0, len(raw_chunks) - 1):
       first_comma = raw_chunks[i].find(',')
       index = raw_chunks[i][0:first_comma]
       chunk_path = raw_chunks[i][first_comma + 1: -1]
       chunk_hash = hash_file(folder + '/' + chunk_path)
       parsed_chunks.append((index, chunk_hash))
       chunk_set.add(index)
       
print(parsed_chunks)

# intializing client socket and establishing connection
tracker_socket = socket(AF_INET, SOCK_STREAM)
tracker_socket.connect(("127.0.0.1", 5100))

# generating local chunks messages and updating P2PTracker about local chunks
for chunk in parsed_chunks:
    chunk_index, chunk_hash = chunk[0], chunk[1]   
    message = ("LOCAL_CHUNKS", chunk_index, chunk_hash, client_ip, client_port)
    message = ",".join(message)
    log = (client_name, "LOCAL_CHUNKS", str(chunk_index), chunk_hash, "localhost", str(client_port))
    log = ",".join(log)
    logger.info(log)
    time.sleep(0.1)
    tracker_socket.send(message.encode())


# asking P2PTracker where missing chunks are
def tracker():
    while(True):
        for i in range(1, total_num_chunks + 1):
            if str(i) not in chunk_set and str(i) not in temp_set:
                message = ("WHERE_CHUNK", str(i))
                message = ",".join(message)
                log = (client_name, "WHERE_CHUNK", str(i))
                log = ",".join(log)
                logger.info(log)
                time.sleep(0.1)
                tracker_socket.send(message.encode())
                res = tracker_socket.recv(4096).decode()
                res = res.split(",")
                if (res[0] == "GET_CHUNK_FROM"):
                    peers = (len(res) - 3) / 2
                    peer_num = random.randint(0, peers - 1)
                    peer_ip = res[peer_num * 2 + 3]
                    peer_port = res[peer_num * 2 + 4]
                    temp_set.add(str(i))
                    peer_thread = threading.Thread(target=receive, args=(peer_ip, peer_port, i,))
                    peer_thread.start()
        time.sleep(5)

# receieves file from another peer
def receive(peer_ip, peer_port, i):
    request_socket = socket(AF_INET, SOCK_STREAM)
    print("peer ip: " + peer_ip + ", peer port: " + peer_port)
    request_socket.connect((peer_ip, int(peer_port)))
    chunk_index = str(i)
    message = ("REQUEST_CHUNK", chunk_index)
    message = ",".join(message)
    log = (client_name, "REQUEST_CHUNK", str(chunk_index), "localhost", str(peer_port))
    log = ",".join(log)
    logger.info(log)
    request_socket.send(message.encode())
    fpath = folder + "/chunk_" + chunk_index
    filesize = int(request_socket.recv(1024).decode())
    with open(fpath, 'wb') as file:
        bytes = 0
        while bytes < filesize:
            buffer = request_socket.recv(1024)
            if not buffer:
                break
            file.write(buffer)
            bytes += len(buffer)
    temp_set.remove(str(i))
    chunk_set.add(str(i))
    chunk_hash = hash_file(fpath)
    message = ("LOCAL_CHUNKS", chunk_index, chunk_hash, client_ip, client_port)
    message = ",".join(message)
    log = (client_name, "LOCAL_CHUNKS", str(chunk_index), chunk_hash, "localhost", str(client_port))
    log = ",".join(log)
    logger.info(log)
    time.sleep(0.1)
    tracker_socket.send(message.encode())

    

peer_socket = socket(AF_INET, SOCK_STREAM)
peer_socket.bind((client_ip, int(client_port)))
peer_socket.listen(1)

# sends files to another peer
def send():
    while(True):
        send_socket, addr = peer_socket.accept()
        message = send_socket.recv(1024).decode()
        message = message.split(",")
        fpath = folder + '/chunk_' + message[1]
        filesize = os.path.getsize(fpath)
        send_socket.send(str(filesize).encode())
        with open(fpath, 'rb') as file:
            bytes = 0
            while bytes < filesize:
                buffer = file.read(1024)
                send_socket.sendall(buffer)
                bytes += len(buffer)

tracker_thread = threading.Thread(target=tracker)
send_thread = threading.Thread(target=send)
tracker_thread.start()
send_thread.start()

if __name__ == "__main__":
	pass