import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

def send_email_with_attachment(file_path):
    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = "dataupdate43@gmail.com"
    msg['To'] = "samargrag011@gmail.com"
    msg['Subject'] = "data backup"

    # Attach the body of the email
    msg.attach(MIMEText("Test", 'plain'))

    # Attach the file
    attachment = open(file_path, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(file_path)}')
    msg.attach(part)

    # Connect to the SMTP server and send the email
    try:
        server = smtplib.SMTP('smtp.your-email-provider.com', 587)  # Use your email provider's SMTP server and port
        server.starttls()
        server.login("dataupdate43@gmail.com", "xzcy wykh elqk ejtw")
        text = msg.as_string()
        server.sendmail("dataupdate43@gmail.com", "samargrag011@gmail.com", text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")