import argparse
import smtplib
from email.message import EmailMessage


FROM_EMAIL = "phatyerto@gmail.com"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_LOGIN = "phatyerto@gmail.com"

#python3 mail_client.py phatyerto@gmail.com "Test txt" txt "Hello" "APP_PASSWORD"
#python3 mail_client.py phatyerto@gmail.com "Test html" html "<h1>Hello</h1>" "APP_PASSWORD"

parser = argparse.ArgumentParser()
parser.add_argument("to")
parser.add_argument("subject")
parser.add_argument("format", choices=["txt", "html"])
parser.add_argument("body")
parser.add_argument("app_password")
args = parser.parse_args()

message = EmailMessage()
message["From"] = FROM_EMAIL
message["To"] = args.to
message["Subject"] = args.subject

if args.format == "txt":
    message.set_content(args.body)
else:
    message.set_content("Not support HTML")
    message.add_alternative(args.body, subtype="html")

with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
    smtp.login(SMTP_LOGIN, args.app_password)
    smtp.send_message(message)

print("Письмо отправлено")
