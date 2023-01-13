import random
import time
import sys
from socket import *

# Create UDP socket
serverSocket = socket(AF_INET, SOCK_DGRAM)
# Assign IP address and port number to socket
serverSocket.bind(('', 9093))
# Assign Loss and Delay parameters
LOSS_RATE = .05
AVERAGE_DELAY = 400

# Open file for writing in byte mode
f = open("outputfile.txt", "wb")

# Variable to hold expected sequence number 
expect = 0

while True:
	rand = random.uniform(0, 1)
	# Receive the client packet along with the address it is coming from
	message, address = serverSocket.recvfrom(1024)

	# Decide whether to reply, or simulate packet loss. If rand is less than LOSS_RATE, we consider the packet lost and do not respond
	if rand < LOSS_RATE:
	   print("Lost packet or ACK")
	   continue

	# Simulate network delay.
	delay = random.randint(0.0, 2*AVERAGE_DELAY)
	print(delay)
	time.sleep(delay/1000);

	# Last packet sent and if it is in correct order, write to file, then close file
	if(sys.getsizeof(message)<513 and (expect == message[0])):
		f.write(message[1:])
		# Send ACK
		print("ACK {} sent".format(message[0]))
		serverSocket.sendto(message[0].to_bytes(1, "big"), address)
		f.close()
		break
	# Check if packet header matches what receiver is expecting
	elif(expect == message[0]):
		f.write(message[1:])
		# Send ACK
		print("ACK {} sent".format(message[0]))
		serverSocket.sendto(message[0].to_bytes(1, "big"), address)
		# Update expected sequence number
		expect = abs(expect-1)
	# Receive duplicate therefore send ACK, but do not write into file
	elif(expect != message[0]):
		#Send ACK
		print("ACK {} sent".format(message[0]))
		serverSocket.sendto(message[0].to_bytes(1, "big"), address)