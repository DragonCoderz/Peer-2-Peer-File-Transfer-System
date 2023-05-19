import socket
# import argparse
import threading
import sys
import hashlib
import time
import logging
import random


#TODO: Implement P2PClient that connects to P2PTracker
logging.basicConfig(filename="logs.log", format="%(message)s", filemode="a")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# python3 P2PClient.py -folder /Users/vedicpanda/Desktop/PA2/folder1 -transfer_port 9090 -name Yash 
# python3 P2PClient.py -folder /Users/vedicpanda/Desktop/PA2/folder2 -transfer_port 1050 -name Vedic
# python3 P2PClient.py -folder /Users/vedicpanda/Desktop/PA2/folder3 -transfer_port 1101 -name Aazia
#p2pclient.py -folder <my-folderfull-path> -transfer_port <transfer-port-num> -name <entity-name>
folder_path = str(sys.argv[2])
local_chunk_path = folder_path + '/local_chunks.txt'
transfer_port = int(sys.argv[4])
client_name = str(sys.argv[6])
trackerPort = 5100
ip_address = 'localhost'

#Create socket to allow p2pclient to connect to tracker
client2tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client2tracker.connect(('localhost', trackerPort))

#Create socket to allow client to host connections to other clients
clienthost2client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clienthost2client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
clienthost2client.bind((ip_address, transfer_port)) #binds the client to the host and IP address
clienthost2client.listen() #puts our client into listening mode for new connections

#create socket to allow client to communicate to a client host
client2hostclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

filesToBeHashed = []
indicesWeHave = []
totalChunks = []

def hash_file(filename):
   """"This function returns the SHA-1 hash
   of the file passed into it"""

   # make a hash object
   h = hashlib.sha1()

   # open file for reading in binary mode
   with open(filename,'rb') as file:

       # loop till the end of the file
       chunk = 0
       while chunk != b'':
           # read only 1024 bytes at a time
           chunk = file.read(1024)
           h.update(chunk)

   # return the hex representation of digest
   return h.hexdigest()

#open local chunks and get a list of files to be hashed and sent over

def computeSendAndStoreHashes():
    # path_to_be_hashed = folder_path + '/local_chunks.txt'
    with open(local_chunk_path, 'r') as lc:
           for line in lc.readlines():
                linecontent = str(line).strip().split(',')
                if (linecontent[1].strip() == 'LASTCHUNK'):
                        #Have a list that contains all possible indices so we can then later compare with the list of indices we currently have and request them later
                        totalChunks.extend(list(range(1, int(linecontent[0])+1)))
                        break
                else:							
                    #filesToBeHashed Entry Format: (index, chunk file name)
                    #format: LOCAL_CHUNKS,<chunk_index>,<file_hash>,<IP_address>,<Port_number>
                    local_message = 'LOCAL_CHUNKS,'
                    local_message += linecontent[0] + ','
                    path_to_curr_chunk = folder_path + '/' + str(linecontent[1]).strip()
                    hash = hash_file(path_to_curr_chunk)
                    local_message += str(hash) + ','
                    local_message += str(ip_address) + ',' + str(transfer_port)
                    local_message = local_message.strip()
                    logger.info(client_name+',' + local_message)
                    client2tracker.send(local_message.encode('ascii'))
                    indicesWeHave.append(int(linecontent[0]))
                    time.sleep(1)

        
#request what we don't have 
#format WHERE_CHUNK,<chunk_index>
def requestChunk():
    indicesWeDontHave = list((set(totalChunks) - set(indicesWeHave)))
    while len(indicesWeDontHave) > 0:
        for chunk_index in indicesWeDontHave:
            where_message = "WHERE_CHUNK,"
            where_message += str(chunk_index)
            logger.info(client_name+',' + where_message)
            client2tracker.send(where_message.encode('ascii'))
            time.sleep(1)
            where_response = client2tracker.recv(1024).decode('ascii').strip()
            where_response = where_response.split(',')
            if where_response[0] == 'CHUNK_LOCATION_UNKNOWN':
                    continue
            else:
                    ##GET_CHUNK_FROM,<chunk_index>,<file_hash>,<IP_address1>,<Port_number1>
                    possible_request_locations = list(range(3, len(where_response), 2))
                    #['GET_CHUNK_FROM', '1', '68b94c96411d22a26a46c1029670d0a3236dee04', 'localhost', '9090CHUNK_LOCATION_UNKNOWN', '1WHERE_CHUNK']
                    randomIndex = random.randrange(0, len(possible_request_locations))
                    ip_to_query = where_response[possible_request_locations[randomIndex]]
                    port_to_query = where_response[possible_request_locations[randomIndex]+1]
                    client2hostclient.connect((ip_to_query,int(port_to_query))) 
                    #where_response[3] = ip_address, where_response[4] = port_number
                    request_message = 'REQUEST_CHUNK,'+str(chunk_index)+','+ip_to_query+','+port_to_query

                    logger.info(client_name+',' + request_message)

                    client2hostclient.send(request_message.encode('ascii'))
                    time.sleep(1)
                    new_chunk_file_name = "chunk_" + where_response[1]
                    new_chunk_file_path = folder_path + '/' + new_chunk_file_name
                    request_response = client2hostclient.recv(1024)
                    new_chunk_file_content = open(new_chunk_file_path,'wb')
                    #keep writing into the file until host peer says it's done sending stuff
                    while(request_response):
                            print("request response")
                            print(request_response)
                            new_chunk_file_content.write(request_response)
                            request_response = client2hostclient.recv(1024)
                    new_chunk_file_content.close()

                    new_file_hash = hash_file(new_chunk_file_path)
                    #reminder of local chunk format: LOCAL_CHUNKS,<chunk_index>,<file_hash>,<IP_address>,<Port_number>
                    update_message = 'LOCAL_CHUNKS,'+str(chunk_index)+','+str(new_file_hash)+','+str(ip_address)+','+str(transfer_port)
                    client2tracker.send(update_message.encode('ascii'))
                    time.sleep(1)
                    indicesWeHave.append(chunk_index)
                    indicesWeDontHave.remove(chunk_index)
                    continue
    print("Done with requesting files")

#send over file upon request
def receive_and_send():
    while True:
        peer_socket, peer_port = clienthost2client.accept()
        peer_request = peer_socket.recv(1024).decode('ascii')
        #peer_request format: REQUEST_CHUNK,<chunk_index>
        
        peer_request = peer_request.strip().split(',')
        if peer_request[0] == "REQUEST_CHUNK":
            indexToSend = peer_request[1]

            # lo_ch = open(local_chunk_path, 'r')
            # for line in lo_ch.readlines():
            #         index, filename = line.split(',')
            #         if index == indexToSend:
            #                 print("correct file is found in receiver/sender")
            #                 chunk_to_send_file_name = filename
            #                 break
            # lo_ch.close()

            chunk_to_send_path = folder_path + '/chunk_' + indexToSend
            with open(chunk_to_send_path, 'rb') as chunk_to_send_content:
                content = chunk_to_send_content.read(1024)
                while content:
                        peer_socket.send(content)
                        time.sleep(0.5)
                        content = chunk_to_send_content.read(1024)
            #Done to signifiy that file sending process is over and that the connection is about to close so we shouldn't keep reading
            peer_socket.close()

def request():
        while True:
                receiveThread = threading.Thread(target=receive_and_send)
                receiveThread.start()
                # requestChunk()
                # receive_and_send()

if __name__ == "__main__":
    computeSendAndStoreHashes()
    requestThread = threading.Thread(target=requestChunk)
    requestThread.start()
    request()