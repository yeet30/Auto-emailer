from flask import Flask, request, jsonify
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pytz
import pycountry
import smtplib

app = Flask(__name__)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def get_timezone_from_country(country_name):
    try:
        country = pycountry.countries.get(name=country_name)
        if not country:
            return "UTC"
        timezones = pytz.country_timezones.get(country.alpha_2)
        return timezones[0] if timezones else "UTC"
    except:
        return "UTC"

def send_email(to_email, subject, body, gmail_address, app_password, custom_domain_email):
    msg = MIMEMultipart()
    msg["From"] = f"Pepsites <{custom_domain_email}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(gmail_address, app_password)
            server.sendmail(custom_domain_email, to_email, msg.as_string())
        print(f"✅ Email sent to {to_email} from {custom_domain_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        return False

@app.route('/send', methods=['POST'])
def send_emails():
    data = request.get_json()

    # Campaign parameters from JSON
    gmail_address = data.get("gmail_address")
    app_password = data.get("app_password")
    custom_domain = data.get("custom_domain")
    text1 = data.get("text1")
    text2 = data.get("text2")
    subject1 = data.get("subject1")
    subject2 = data.get("subject2")
    send_hour = data.get("send_hour", 12)
    send_minute = data.get("send_minute", 0)
    mail_amount = data.get("mail_amount", 10)
    contacts = data.get("contacts", [])

    sent_count = 0
    sent_list = []

    for contact in contacts:
        if sent_count >= mail_amount:
            break

        name = contact.get("name")
        email = contact.get("email")
        country = contact.get("country")
        has_website = contact.get("hasWebsite", False)

        timezone_str = get_timezone_from_country(country)
        now = datetime.now(pytz.timezone(timezone_str))

        print(f"🌍 {name} ({country}) → Local Time: {now.hour:02d}:{now.minute:02d}")

        if now.hour == send_hour and now.minute == send_minute:
            subject = subject1 if has_website else subject2
            body = text1 if has_website else text2
            personalized_body = body.replace("{name}", name)

            success = send_email(email, subject, personalized_body, gmail_address, app_password, custom_domain)
            if success:
                sent_count += 1
                sent_list.append(email)

    return jsonify({
        "status": "ok",
        "sent": sent_list,
        "total_sent": sent_count
    })

if __name__ == '__main__':
    app.run(port=5000)
