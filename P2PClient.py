from socket import *
import argparse
import threading
import sys
import hashlib
import time
import logging

# parsing command line arguments
# p2pclient.py -folder <my-folder-full-path> -transfer_port <transfer-port-num> -name <entity-name>

parser = argparse.ArgumentParser()
parser.add_argument('-folder')
parser.add_argument('-transfer_port')
parser.add_argument('-name')
args = parser.parse_args()
# path to folder with chunk data, port for connecting with other clients, name of client for logging
folder, transfer_port, client_name = args.folder, args.transfer_port, args.name

# parsing local_chunks.txt and extracting lines
# var chunks is a list of each line in txt as strings
with open(folder+'\\local_chunks.txt') as file:
	raw_chunks = file.readlines()

fileset_size = int(raw_chunks[-1][0])


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
       chunk_hash = hash_file(folder + '\\' + chunk_path)
       parsed_chunks.append((index, chunk_hash))
       

# intializing client socket and establishing connection
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(("127.0.0.1", 5100))


if __name__ == "__main__":
	pass