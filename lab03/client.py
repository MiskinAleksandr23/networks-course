import socket
import sys


def main():
    if len(sys.argv) != 4:
        print("Incorrect: python3 client.py server_host server_port filename")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    filename = sys.argv[3]

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    request = (
        f"GET /{filename} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    client_socket.sendall(request.encode("utf-8"))

    response = b""
    while True:
        data = client_socket.recv(4096)
        if not data:
            break
        response += data

    print(response.decode("utf-8"))
    client_socket.close()


if __name__ == "__main__":
    main()
