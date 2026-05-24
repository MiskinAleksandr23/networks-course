import argparse
import os
import select
import socket
import struct
import time


ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0
ICMP_TIME_EXCEEDED = 11


def checksum(data):
    if len(data) % 2 == 1:
        data += b"\x00"

    total = 0
    for i in range(0, len(data), 2):
        total += (data[i] << 8) + data[i + 1]
        total = (total & 0xffff) + (total >> 16)

    return ~total & 0xffff


def make_packet(identifier, sequence):
    data = struct.pack("!d", time.time())
    header = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, 0, identifier, sequence)
    packet_checksum = checksum(header + data)
    header = struct.pack(
        "!BBHHH",
        ICMP_ECHO_REQUEST,
        0,
        packet_checksum,
        identifier,
        sequence,
    )
    return header + data


def trace(host, max_ttl, probes, timeout):
    destination = socket.gethostbyname(host)
    identifier = os.getpid() & 0xffff

    print(f"traceroute to {host} ({destination}), {max_ttl} hops max")

    for ttl in range(1, max_ttl + 1):
        print(f"{ttl:2}", end="  ")
        reached = False

        for probe in range(1, probes + 1):
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
            sock.settimeout(timeout)

            sequence = ttl * 100 + probe
            packet = make_packet(identifier, sequence)
            start = time.time()
            sock.sendto(packet, (destination, 0))

            ready = select.select([sock], [], [], timeout)
            if not ready[0]:
                print("*", end="  ")
                sock.close()
                continue

            reply, address = sock.recvfrom(1024)
            rtt = (time.time() - start) * 1000
            ip_header_length = (reply[0] & 0x0f) * 4
            icmp_type = reply[ip_header_length]

            print(f"{address[0]} {rtt:.2f} ms", end="  ")

            if icmp_type == ICMP_ECHO_REPLY:
                reached = True

            sock.close()

        print()

        if reached:
            break


parser = argparse.ArgumentParser()
parser.add_argument("host")
parser.add_argument("-m", "--max-ttl", type=int, default=30)
parser.add_argument("-p", "--probes", type=int, default=3)
parser.add_argument("-t", "--timeout", type=float, default=1)
args = parser.parse_args()

trace(args.host, args.max_ttl, args.probes, args.timeout)
