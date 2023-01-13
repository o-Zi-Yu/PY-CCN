# receiver.py - The receiver in the reliable data transer protocol
import socket
import sys
import random

serverIP = sys.argv[1]
RECEIVER_ADDR = (serverIP, 9093)

LOSS_RATE = 0

# send with possible loss
def udtsend(packet, sock, addr):
    # simulate packet loss
    if random.uniform(0, 1) > LOSS_RATE:
        sock.sendto(packet, addr)
    return

# receive
def recv(sock):
    packet, addr = sock.recvfrom(1024)
    return packet, addr

# create packet with big median sequence number
def make(seq_num, data=b''):
    seq_bytes = seq_num.to_bytes(8, byteorder='big', signed=True)
    return seq_bytes + data

# empty packet
def make_empty():
    return b''

# extract sequence number
def extract(packet):
    seq_num = int.from_bytes(packet[0:8], byteorder='big', signed=True)
    return seq_num, packet[8:]

# Receive packets from the sender
def receive(sock, filename):
    # Open the file for writing
    file = open(filename, 'wb')
    
    expected_num = 0
    while True:
        # Get the next packet from the sender
        pkt, addr = recv(sock)
        if not pkt:
            break
        seq_num, data = extract(pkt)
        
        # Send back an ACK
        if seq_num == expected_num:
            pkt = make(expected_num)
            udtsend(pkt, sock, addr)
            expected_num += 1
            file.write(data)
        else:
            pkt = make(expected_num - 1)
            udtsend(pkt, sock, addr)

    file.close()


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(RECEIVER_ADDR) 
    filename = "outputfile.txt"
    receive(sock, filename)
    sock.close()