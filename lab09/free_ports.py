import socket
import sys


host = sys.argv[1]
start_port = int(sys.argv[2])
end_port = int(sys.argv[3])

for port in range(start_port, end_port + 1):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()

    if result != 0:
        print(port)
