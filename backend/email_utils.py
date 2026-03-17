import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ===== CONFIGURE YOUR EMAIL =====
SENDER_EMAIL = "srustishettym@gmail.com"       # Replace with your Gmail
APP_PASSWORD = "npsi wozj soxz axjs"   # Gmail App Password (2FA required)

def send_email(to_email, subject, body):
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to Gmail SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
