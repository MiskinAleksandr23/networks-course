import socket
from urllib.parse import urlsplit


HOST = "127.0.0.1"
PORT = 8889
BUFFER_SIZE = 4096


proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
proxy_socket.bind((HOST, PORT))
proxy_socket.listen(5)

print(f"Proxy is running on http://{HOST}:{PORT}")


def send_error(client_socket, status_code, text):
    body = text.encode("utf-8")
    response = (
        f"HTTP/1.1 {status_code}\r\n"
        "Content-Type: text/plain; charset=utf-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("utf-8") + body

    
    client_socket.sendall(response)


def write_log(url, status_code):
    with open("proxy.log", "a", encoding="utf-8") as log_file:
        log_file.write(f"{url} {status_code}\n")


while True:
    client_socket, client_address = proxy_socket.accept()
    print(f"Client connected: {client_address}")

    try:
        request = client_socket.recv(BUFFER_SIZE).decode("iso-8859-1")
        first_line = request.splitlines()[0]
        method, raw_url, _ = first_line.split()

        if method != "GET":
            send_error(client_socket, "405 Method Not Allowed Error", "Only GET is supported\n")
            write_log(raw_url, 405)
            client_socket.close()
            continue

        if raw_url.startswith("/"):
            raw_url = raw_url[1:]
        if not raw_url.startswith("http://"):
            raw_url = "http://" + raw_url

        url = urlsplit(raw_url)
        path = url.path or "/"
        if url.query:
            path += "?" + url.query

        web_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        web_socket.connect((url.hostname, url.port or 80))

        web_request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {url.netloc}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        web_socket.sendall(web_request.encode("iso-8859-1"))

        response = web_socket.recv(BUFFER_SIZE)
        if not response:
            send_error(client_socket, "502 Bad Gateway Error", "Empty response from server\n")
            write_log(raw_url, 502)
            web_socket.close()
            client_socket.close()
            continue

        status_code = response.split(b" ")[1].decode("iso-8859-1")
        write_log(raw_url, status_code)

        client_socket.sendall(response)

        while True:
            response = web_socket.recv(BUFFER_SIZE)
            if not response:
                break
            client_socket.sendall(response)

        web_socket.close()
        print(f"{method} {raw_url} -> {status_code}")
    except Exception as error:
        send_error(client_socket, "502 Bad Gateway Error", f"{error}\n")
        write_log("error", 502)

    client_socket.close()
