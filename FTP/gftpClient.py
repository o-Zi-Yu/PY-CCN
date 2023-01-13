import socket
import sys
import _thread
import time
import random

# input argument is 2
if (len(sys.argv) != 3):
    print("args: ip, windowsize")
    exit(0)

serverIP = sys.argv[1]
WINDOW_SIZE = int(sys.argv[2])


PACKET_SIZE = 512
RECEIVER_ADDR = (serverIP, 9093)
SENDER_ADDR = (serverIP, 0)

LOSS_RATE = 0.05 #customize
AVERAGE_DELAY = 100 #customize
delay = random.randint(0.0, 2*AVERAGE_DELAY) #randomize delay

# Set up sleep time for delay based on average delay
SLEEP_INTERVAL = delay/1000
TIMEOUT_INTERVAL = 1


# Timer class
class Timer(object):
    TIMER_STOP = -1

    def __init__(self, duration):
        self._start_time = self.TIMER_STOP
        self._duration = duration

    # Starts the timer
    def start(self):
        if self._start_time == self.TIMER_STOP:
            self._start_time = time.time()

    # Stops the timer
    def stop(self):
        if self._start_time != self.TIMER_STOP:
            self._start_time = self.TIMER_STOP

    # Determines whether the timer is runnning
    def running(self):
        return self._start_time != self.TIMER_STOP

    # Determines whether the timer timed out
    def timeout(self):
        if not self.running():
            return False
        else:
            return time.time() - self._start_time >= self._duration

    def origintime(self):
        self._origin_time = time.time()

    #calculates total time of the ftp
    def totaltime(self):
        return time.time() - self._origin_time



base = 0
mutex = _thread.allocate_lock()
send_timer = Timer(TIMEOUT_INTERVAL)


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

# setup window size
def set_window_size(num_packets):
    global base
    return min(WINDOW_SIZE, num_packets - base)

# Send packet
def send(sock, filename):
    global mutex
    global base
    global send_timer

    file = open(filename, 'rb')

    packets = []
    seq_num = 0
    while True:
        data = file.read(PACKET_SIZE)
        if not data:
            break
        packets.append(make(seq_num, data))
        seq_num += 1

    num_packets = len(packets)
    window_size = set_window_size(num_packets)
    next_to_send = 0
    base = 0

    # Start the receiver thread
    _thread.start_new_thread(receive, (sock,))

    while base < num_packets:
        mutex.acquire()
        # Send all the packets in the window
        while next_to_send < base + window_size:
            udtsend(packets[next_to_send], sock, RECEIVER_ADDR)
            next_to_send += 1

        # Start the timer
        if not send_timer.running():
            send_timer.start()

        # Wait until a timer goes off or we get an ACK
        while send_timer.running() and not send_timer.timeout():
            mutex.release()
            time.sleep(SLEEP_INTERVAL)
            mutex.acquire()

        if send_timer.timeout():
            send_timer.stop()
            next_to_send = base
        else:
            window_size = set_window_size(num_packets)
        mutex.release()

    # Send empty packet as sentinel
    udtsend(make_empty(), sock, RECEIVER_ADDR)
    file.close()

# Receive thread
def receive(sock):
    global mutex
    global base
    global send_timer

    while True:
        pkt, _ = recv(sock)
        ack, _ = extract(pkt)

        if (ack >= base):
            mutex.acquire()
            base = ack + 1
            send_timer.stop()
            transferTime = send_timer.running()
            mutex.release()


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SENDER_ADDR)
    filename = "inputfile.txt"
    send_timer.origintime()
    send(sock, filename)
    transferTime = send_timer.totaltime()
    print("sFTP: file sent successfully to {} in {:.3f}secs".format(
        serverIP, transferTime))
    file1 = open("myfile.txt", "a")  # append mode
    file1.write(str(transferTime)+"\n")
    sock.close()
    file1.close()
