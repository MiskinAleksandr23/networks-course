import random
import socket


HOST = "127.0.0.1"
PORT = 12000


server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print(f"UDP server is running on {HOST}:{PORT}")

while True:
    message, address = server_socket.recvfrom(1024)

    if random.random() < 0.2:
        print(f"Lost packet from {address}: {message.decode()}")
        continue

    response = message.decode().upper()
    server_socket.sendto(response.encode(), address)
    print(f"Answered to {address}: {response}")
