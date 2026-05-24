import argparse
import socket
from pathlib import Path


HOST = "127.0.0.1"
PORT = 12000
CHUNK_SIZE = 512
TIMEOUT = 1.0


parser = argparse.ArgumentParser()
parser.add_argument("file")
parser.add_argument("--host", default=HOST)
parser.add_argument("--port", type=int, default=PORT)
parser.add_argument("--chunk-size", type=int, default=CHUNK_SIZE)
parser.add_argument("--timeout", type=float, default=TIMEOUT)
args = parser.parse_args()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(args.timeout)

data = Path(args.file).read_bytes()
chunks = [data[i:i + args.chunk_size] for i in range(0, len(data), args.chunk_size)]

seq = 0

for index, chunk in enumerate(chunks):
    is_last = index == len(chunks) - 1
    packet = bytes([seq, int(is_last)]) + chunk

    while True:
        client_socket.sendto(packet, (args.host, args.port))
        print(f"sent packet {seq}, {len(chunk)} bytes")

        try:
            ack, _ = client_socket.recvfrom(1024)
            if ack.decode() == f"ACK {seq}":
                print(f"received ACK {seq}")
                seq = 1 - seq
                break
        except socket.timeout:
            print("timeout, resend")

client_socket.close()
print("done")
