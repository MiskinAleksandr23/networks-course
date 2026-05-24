import socket
import time


HOST = "127.0.0.1"
PORT = 12000
TIMEOUT = 1


client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(TIMEOUT)

rtts = []
lost = 0

for number in range(1, 11):
    send_time = time.time()
    message = f"Ping {number} {send_time}"

    client_socket.sendto(message.encode(), (HOST, PORT))

    try:
        response, _ = client_socket.recvfrom(1024)
        rtt = time.time() - send_time
        rtts.append(rtt)
        print(f"{response.decode()} RTT={rtt:.6f} sec")
    except socket.timeout:
        lost += 1
        print("Request Timed out")

client_socket.close()

print()
print("--- ping statistics ---")
print(f"10 packets transmitted, {10 - lost} received, {lost * 10}% packet loss")

if rtts:
    min_rtt = min(rtts)
    avg_rtt = sum(rtts) / len(rtts)
    max_rtt = max(rtts)
    print(f"rtt min/avg/max = {min_rtt:.6f}/{avg_rtt:.6f}/{max_rtt:.6f} sec")
