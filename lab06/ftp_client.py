import argparse
from ftplib import FTP
from pathlib import Path


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 2021
DEFAULT_USER = "TestUser"
DEFAULT_PASSWORD = "12345"


def connect(args):
    ftp = FTP()
    ftp.connect(args.host, args.port)
    ftp.login(args.user, args.password)
    return ftp


parser = argparse.ArgumentParser(description="Simple FTP client")
parser.add_argument("--host", default=DEFAULT_HOST)
parser.add_argument("--port", type=int, default=DEFAULT_PORT)
parser.add_argument("--user", default=DEFAULT_USER)
parser.add_argument("--password", default=DEFAULT_PASSWORD)

subparsers = parser.add_subparsers(dest="command", required=True)

subparsers.add_parser("list")

upload_parser = subparsers.add_parser("upload")
upload_parser.add_argument("local_file")
upload_parser.add_argument("remote_file", nargs="?")

download_parser = subparsers.add_parser("download")
download_parser.add_argument("remote_file")
download_parser.add_argument("local_file", nargs="?")

args = parser.parse_args()
ftp = connect(args)

if args.command == "list":
    ftp.retrlines("LIST")

if args.command == "upload":
    local_file = Path(args.local_file)
    remote_file = args.remote_file or local_file.name
    with local_file.open("rb") as file:
        ftp.storbinary(f"STOR {remote_file}", file)

    print(f"Uploaded {local_file} -> {remote_file}")

if args.command == "download":
    local_file = Path(args.local_file or args.remote_file)
    with local_file.open("wb") as file:
        ftp.retrbinary(f"RETR {args.remote_file}", file.write)
    print(f"Downloaded {args.remote_file} -> {local_file}")
ftp.quit()
