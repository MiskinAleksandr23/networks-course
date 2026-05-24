import argparse
import os
import select
import socket
import struct
import time


ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0


def checksum(data):
    if len(data) % 2 == 1:
        data += b"\x00"

    total = 0
    for i in range(0, len(data), 2):
        total += (data[i] << 8) + data[i + 1]
        total = (total & 0xffff) + (total >> 16)

    return ~total & 0xffff


def make_packet(identifier, sequence):
    data = struct.pack("!d", time.time()) + b"simple icmp ping"
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


def ping(host, count, timeout):
    address = socket.gethostbyname(host)

    identifier = os.getpid() & 0xffff

    print(f"PINGING {host} ({address})")
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    rtts = []
    received = 0

    for sequence in range(1, count + 1):
        packet = make_packet(identifier, sequence)
        start = time.time()
        sock.sendto(packet, (address, 0))

        ready = select.select([sock], [], [], timeout)
        if not ready[0]:
            print(f"Timeout for icmp_seq {sequence}")
            time.sleep(1)
            continue

        reply, reply_address = sock.recvfrom(1024)
        rtt = (time.time() - start) * 1000

        ip_header_length = (reply[0] & 0x0f) * 4
        icmp_header = reply[ip_header_length:ip_header_length + 8]
        icmp_type, code, _, reply_id, reply_seq = struct.unpack("!BBHHH", icmp_header)

        if icmp_type == ICMP_ECHO_REPLY and reply_id == identifier:
            received += 1
            rtts.append(rtt)
            print(
                f"{len(reply) - ip_header_length} bytes from {reply_address[0]}: "
                f"icmp_seq={reply_seq} time={rtt:.3f} ms"
            )
        else:
            print(f"ICMP type={icmp_type} code={code} from {reply_address[0]}")
        time.sleep(1)
    sock.close()

    loss = (count - received) / count * 100
    print()
    print(f"--- {host} ping statistics ---")
    print(f"{count} packets transmitted, {received} received, {loss:.1f}% packet loss")

    if rtts:
        min_rtt = min(rtts)
        avg_rtt = sum(rtts) / len(rtts)
        max_rtt = max(rtts)
        print(f"rtt min/avg/max = {min_rtt:.3f}/{avg_rtt:.3f}/{max_rtt:.3f} ms")


parser = argparse.ArgumentParser()
parser.add_argument("host")
parser.add_argument("-c", "--count", type=int, default=4)
parser.add_argument("-t", "--timeout", type=float, default=1)
args = parser.parse_args()

ping(args.host, args.count, args.timeout)
