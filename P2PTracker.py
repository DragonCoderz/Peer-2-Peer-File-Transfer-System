import socket
import argparse
import threading
import sys
import hashlib
import time
import logging


#TODO: Implement P2PTracker
logging.basicConfig(filename="logs.log", format="%(message)s", filemode="a")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


check_list = {}
chunk_list = {}

p2ptracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
p2ptracker.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
p2ptracker.bind(('localhost', 5100)) #binds the server to the host and IP address
p2ptracker.listen() #puts our server into listening mode for new connections


#Receive Condition

#potential message formats:
#LOCAL_CHUNKS,<chunk_index>,<file_hash>,<IP_address>,<Port_number>
#REQUEST_CHUNK,<chunk_index>
#WHERE_CHUNK,<chunk_index>

def handle(p2pclient):
	while True:
		# print("Runs3")
		message = p2pclient.recv(1024).decode('ascii')
		message = message.split(',')
		if message[0] == 'LOCAL_CHUNKS':
			print(message)
			chunk_index = message[1]
			file_hash = message[2]
			ip_address = message[3]
			port_number = message[4]
			#check list dict entry: 
			#key: (chunk_index, file_hash)
			#value: (ip address, port number)
			#chunk list dict entry:
			#key: chunk_index
			#value (ip_address, port_number, file_hash)
			if (chunk_index, file_hash) in check_list:
				if chunk_index not in chunk_list:
					# chunk_list[chunk_index] = []
					chunk_list[chunk_index] = [(check_list[(chunk_index, file_hash)][0], check_list[(chunk_index, file_hash)][1], file_hash)]
				else:
					chunk_list[chunk_index].append((ip_address, port_number, file_hash))
					#chunk_list[chunk_index].append(ip_address)
					#chunk_list[chunk_index].append(port_number)
					#chunk_list[chunk_index].append(file_hash)
			else:
				check_list[(chunk_index, file_hash)] = (ip_address, port_number)
				
		elif message[0] == 'WHERE_CHUNK':
			#response format:
			##GET_CHUNK_FROM,<chunk_index>,<file_hash>,<IP_address1>,<Port_number1>
			# ,<IP_address2>,<Port_number2>,...
			response = "" #line probably not necessary
			# message[1] = chunk_index
			if message[1] in chunk_list:
				file_haash = chunk_list[message[1]][0][2]
				response = "GET_CHUNK_FROM,"+message[1]+','+file_haash+','
				for (ipp, pnn, _) in chunk_list[message[1]]:
						#ipp = ip address, pnn = port number
						response = response + ipp + ',' + pnn + ','
				#print(response)
				response = response[:-1] #removes trailing comma , 

			else:
				response = "CHUNK_LOCATION_UNKNOWN,"+message[1]

			logger.info('P2PTracker,' + response)	
			p2pclient.send(response.encode('ascii'))
			time.sleep(1)

	
def receive():
	while True:
		# print("Runs2")
		tracker_socket, _ = p2ptracker.accept()
		print("new thread being created")
		thread = threading.Thread(target=handle, args=(tracker_socket, ))
		thread.start()

if __name__ == "__main__":
	# print("Runs1")
	receive()
