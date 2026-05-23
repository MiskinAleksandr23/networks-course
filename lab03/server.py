import socket
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor


HOST = "127.0.0.1"


def make_response(status, body):
    headers = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    return headers.encode("utf-8") + body


def handle_client(client_socket, client_address):
    print(f"Connected: {client_address}")

    request = client_socket.recv(4096).decode("utf-8")
    first_line = request.splitlines()[0]
    filename = first_line.split()[1].lstrip("/")

    if filename == "":
        filename = "index.html"

    try:
        with open(filename, "rb") as file:
            body = file.read()
        response = make_response("200 OK", body)
    except FileNotFoundError:
        response = make_response("404 Not Found", b"404 Not Found")

    client_socket.sendall(response)
    client_socket.close()

    # time.sleep(10)


def main():
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print("Incorrect: python3 server.py server_port [concurrency_level]")
        sys.exit(1)

    port = int(sys.argv[1])
    concurrency_level = None
    if len(sys.argv) == 3:
        concurrency_level = int(sys.argv[2])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, port))
    server_socket.listen(5)

    print(f"Running on http://{HOST}:{port}")

    try:
        if concurrency_level is None:
            while True:
                client_socket, client_address = server_socket.accept()
                thread = threading.Thread(
                    target=handle_client,
                    args=(client_socket, client_address),
                )
                thread.start()
        else:
            print(f"Max threads: {concurrency_level}")
            with ThreadPoolExecutor(max_workers=concurrency_level) as pool:
                while True:
                    client_socket, client_address = server_socket.accept()
                    pool.submit(handle_client, client_socket, client_address)
    except KeyboardInterrupt:
        print("\nStopped")

    server_socket.close()


if __name__ == "__main__":
    main()
