import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Gmail SMTP settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
GMAIL_ADDRESS = "pepsites4u@gmail.com"  # Your actual Gmail account
APP_PASSWORD = "xnfu wioy qgiq pgcl"    # Use an App Password
CUSTOM_DOMAIN_EMAIL = "main@pepsites.org"  # Custom domain email

MAIL_SUBJECT = "Want a Free Website Redesign for Your Business?"
MAIL_CONTENT = "Hey there,\n\nI checked out your website for  and love what you’re doing! However I think there’s an opportunity to enhance its design and performance to better attract customers. I’m a web designer, and right now, I’m offering free website redesigns to a few businesses.\n\nI will create a fresh, modern design tailored to your brand—completely free. If you love it, we can discuss how to improve your website further. If not, no worries at all!\n\nWould you be open to a free redesign? Let me know, and I’ll get started right away.\n\n\nBest,\nYiğit\nmain@pepsites.org"

def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = f"Pepsites <{CUSTOM_DOMAIN_EMAIL}>"  # Use your custom domain email, and display your name.
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(GMAIL_ADDRESS, APP_PASSWORD)  # Log in with your Gmail account
            server.sendmail(CUSTOM_DOMAIN_EMAIL, to_email, msg.as_string())
        print(f"✅ Email sent to {to_email} from {CUSTOM_DOMAIN_EMAIL}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")



# Example usage
send_email("yigidoo0424@gmail.com", MAIL_SUBJECT, MAIL_CONTENT)
