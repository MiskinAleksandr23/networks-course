import argparse
import random
import socket


HOST = "127.0.0.1"
PORT = 12000
LOSS = 0.3


parser = argparse.ArgumentParser()
parser.add_argument("--out", default="received.txt")
parser.add_argument("--port", type=int, default=PORT)
args = parser.parse_args()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, args.port))

expected_seq = 0

print(f"Server is running on {HOST}:{args.port}")

with open(args.out, "wb") as file:
    while True:
        packet, address = server_socket.recvfrom(4096)

        if random.random() < LOSS:
            print("lost data packet")
            continue

        if len(packet) < 2:
            print("bad packet")
            continue

        seq = packet[0]
        is_last = packet[1]
        data = packet[2:]

        if seq == expected_seq:
            file.write(data)
            expected_seq = 1 - expected_seq
            print(f"received packet {seq}, {len(data)} bytes")
        else:
            print(f"duplicate packet {seq}")

        if random.random() < LOSS:
            print("lost ACK")
            continue

        server_socket.sendto(f"ACK {seq}".encode(), address)

        if is_last:
            print(f"file saved to {args.out}")
            break

server_socket.close()
