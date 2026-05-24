import socket
import subprocess


interface = "en0"
output = subprocess.check_output(["ifconfig", interface], text=True)

for line in output.splitlines():
    line = line.strip()
    if line.startswith("inet "):
        parts = line.split()
        ip = parts[1]
        netmask_hex = parts[3]
        netmask = int(netmask_hex, 16).to_bytes(4, "big")
        netmask = socket.inet_ntoa(netmask)

        print(f"IP address = {ip}\nNetmask = {netmask}")
        break
