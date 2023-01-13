import time
import sys
from sys import exit
from socket import *

# message for ping
def pingmessage():
        letter = "@"
        return letter*56

#input argument is 2
if (len(sys.argv) != 3):
    print("args: ip, windowsize")
    exit(0)

serverName = sys.argv[1]
serverPort = int(sys.argv[2])

# create a UDP socket
clientSocket = socket(AF_INET, SOCK_DGRAM)

# set server ip
serverIP = gethostbyname(serverName)

pingNum = 0
seqNum = 0

# send a ping 5 times
while pingNum < 5:
	message = pingmessage()
	
	# sends message in byte
	clientSocket.sendto(message.encode(), (serverName, serverPort))
	
	# start timer for rtt
	start = time.perf_counter_ns()
	
	clientSocket.settimeout(1)
	
	try:
		retMessage = clientSocket.recv(128)
	
	except timeout:
		# if nothing recieved from server within 1 second
		print("PING {} {} LOST".format(serverIP, seqNum))
		pingNum += 1
		time.sleep(1)
		continue

	# calculate rtt
	rttEstimate = (time.perf_counter_ns() - start)/1000000

	print("PING {} {} {:.3f}ms".format(serverIP, seqNum, rttEstimate))
	pingNum += 1
	seqNum += 1
	time.sleep(1)


clientSocket.close()