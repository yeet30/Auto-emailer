from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_cors import CORS
import smtplib

app = Flask(__name__)
CORS(app)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

@app.route('/send', methods=['POST'])
def send_email():
    data = request.get_json()
    gmail_address = data.get("base_email")
    sender_name = data.get("sender_name")
    to_email = data.get("to_email")
    app_password = data.get("app_password")
    custom_domain_email = data.get("custom_email")
    subject = data.get("subject")
    body = data.get("body")

    print(data)

    msg = MIMEMultipart()
    msg["From"] = f"{sender_name} <{custom_domain_email}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(gmail_address, app_password)
            server.sendmail(custom_domain_email, to_email, msg.as_string())
        print(f"✅ Email sent to {to_email} from {custom_domain_email} at {datetime.now()}")
        return jsonify({
            "status" : f"Email successfully sent to {to_email} from {custom_domain_email}",
            "isSent" : True,
            "parameters" : [{
                "gmail_address" : gmail_address,
                "custom_domain_email" : custom_domain_email,
                "app_password" : app_password,
                "sender_name" : sender_name,
                "to_email" : to_email,
                "subject" : subject,
                "body" : body,
            }] 
        })
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        return jsonify({
            "status" : f"Failed to send email to {to_email} from {custom_domain_email}",
            "isSent" : False,
            "parameters" : [{
                "gmail_address" : gmail_address,
                "custom_domain_email" : custom_domain_email,
                "app_password" : app_password,
                "sender_name" : sender_name,
                "to_email" : to_email,
                "subject" : subject,
                "body" : body,
            }] 
        })


if __name__ == '__main__':
    app.run(port=5000)
