from socket import *
import time
import sys
import random

# checking command line for correct input
if (len(sys.argv) != 2):
	exit(0)

# initializing server ip address and port number
serverIP = sys.argv[1]
serverPort = 9093

# create a UDP socket
clientSocket = socket(AF_INET, SOCK_DGRAM)

# open the input file to be read in binary form
f = open("inputfile.txt", "rb")


# variable to hold the sequence number
seqNum = 0
# variable to hold indicator that the packet was sent successfully
packetSent = False
# variable to hold indicator that this outgoing packet is the last packet of the file 
lastPacket = False

# timer started for entire file transfer
start = time.perf_counter_ns()

while True:
	# read 479 bytes of data, turns into 512 bytes sent due to overhead in python 
	data = f.read(479)
	# indicate that this is the last packet in the file to be sent
	if(sys.getsizeof(data) < 512):
		lastPacket = True

	seqNumInBytes = seqNum.to_bytes(1, 'big') 
	# creates message with seqNum header and file data
	message = seqNumInBytes + data
	# retrainsmission loop for a max of 6 tries
	for i in range(6):
		packetSent = False
		# send message to server
		clientSocket.sendto(message, (serverIP, serverPort))
		# set timeout for 1 second
		clientSocket.settimeout(1)
		try:
			# get ack from server
			ack = clientSocket.recv(1)
			# check if ack is correct
			if(ack == seqNumInBytes):
				# updates sequence number
				seqNum = abs(1-seqNum)
				# indicate packet was sent successfully
				packetSent = True
				break	
		# if there is a timeout, retransmit
		except timeout:
			continue

	# if last packet is successesfully sent, end while loop 
	if(packetSent and lastPacket):
		transferTime = (time.perf_counter_ns() - start)/1000000000
		print("sFTP: file sent successfully to {} in {:.3f}secs".format(serverIP, transferTime))
		f.close()
		clientSocket.close()
		break
	# if packet has been sent but it is not the last packet, continue sending
	elif(packetSent and not lastPacket):
		continue
	#if any packet was not sent successfully
	else:
		print("sFTP: file transfer unsuccessful: packet retransmission limit reached")
		break