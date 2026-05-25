import argparse
import base64
import socket
import ssl


SENDER = "phatyerto@gmail.com"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


def receive(sock):
    answer = ""
    while True:
        answer += sock.recv(4096).decode("utf-8", errors="ignore")
        lines = answer.splitlines()
        if lines and len(lines[-1]) >= 4 and lines[-1][3] == " ":
            break
    print(answer.splitlines()[0])


def send(sock, command):
    print(command.strip())
    sock.sendall(command.encode("utf-8"))
    receive(sock)


def send_auth(sock, text):
    sock.sendall((base64.b64encode(text.encode()).decode() + "\r\n").encode())
    receive(sock)


parser = argparse.ArgumentParser()
parser.add_argument("recipient")
parser.add_argument("app_password")
parser.add_argument("--host", default=SMTP_HOST)
parser.add_argument("--port", type=int, default=SMTP_PORT)
parser.add_argument("--sender", default=SENDER)
args = parser.parse_args()

body = "Hello!\r\nThis message was sent using raw SMTP over sockets."
message = (
    f"From: {args.sender}\r\n"
    f"To: {args.recipient}\r\n"
    "Subject: Socket SMTP message\r\n"
    "\r\n"
    f"{body}\r\n"
)

raw_sock = socket.create_connection((args.host, args.port))
sock = ssl.create_default_context().wrap_socket(raw_sock, server_hostname=args.host)
receive(sock)

send(sock, "EHLO localhost\r\n")
send(sock, "AUTH LOGIN\r\n")
send_auth(sock, args.sender)
send_auth(sock, args.app_password)
send(sock, f"MAIL FROM:<{args.sender}>\r\n")
send(sock, f"RCPT TO:<{args.recipient}>\r\n")
send(sock, "DATA\r\n")
send(sock, message + ".\r\n")
send(sock, "QUIT\r\n")

sock.close()
print("Message sent")
