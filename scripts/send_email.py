import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys

def send_email(subject, body, to_email, smtp_server, smtp_port, smtp_user, smtp_password):
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # Try SSL first, then fall back to TLS
        try:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        except (ssl.SSLError, ConnectionRefusedError):
            # Fallback to TLS
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)

        print("Email sent successfully")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def main():
    to_email = os.getenv('EMAIL_TO')
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT')
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    subject = os.getenv('EMAIL_SUBJECT')
    body = os.getenv('EMAIL_BODY')

    if not all([to_email, smtp_server, smtp_port, smtp_user, smtp_password, subject, body]):
        print("Error: Missing email configuration environment variables")
        sys.exit(1)

    success = send_email(subject, body, to_email, smtp_server, int(smtp_port), smtp_user, smtp_password)
    if not success:
        print("Failed to send email")
        sys.exit(1)

if __name__ == "__main__":
    main()