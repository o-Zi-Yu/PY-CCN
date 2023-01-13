The test for ping is simple. After running the Server, run the Client and wait for the result.

no packet loss:
PING 127.0.0.1 0 0.177ms
PING 127.0.0.1 1 0.399ms
PING 127.0.0.1 2 1.475ms
PING 127.0.0.1 3 1.040ms
PING 127.0.0.1 4 1.448ms

20% loss and 100ms delay:
PING 127.0.0.1 0 LOST
PING 127.0.0.1 0 125.622ms
PING 127.0.0.1 1 140.118ms
PING 127.0.0.1 2 93.376ms
PING 127.0.0.1 3 203.151ms

PING 127.0.0.1 0 164.610ms
PING 127.0.0.1 1 31.100ms
PING 127.0.0.1 2 31.029ms
PING 127.0.0.1 3 LOST
PING 127.0.0.1 3 139.503ms