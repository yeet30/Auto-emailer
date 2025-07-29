from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pytz
import pycountry
import smtplib
import threading
import time
import json
import os

app = Flask(__name__)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
STATUS_FILE = "campaign_status.json"

campaign_status = ({
    "status": "Has not started yet.",
    "sent": 0,
    "total_sent": 0,
    "next_batch_after": 0
})

def get_timezone_from_country(country_name):
    try:
        country = pycountry.countries.get(name=country_name)
        if not country:
            return "UTC"
        timezones = pytz.country_timezones.get(country.alpha_2)
        return timezones[0] if timezones else "UTC"
    except:
        return "UTC"

def send_email(sender_name, to_email, subject, body, gmail_address, app_password, custom_domain_email):
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
        return True
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        return False

def log_status(data):
    with open(STATUS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def run_email_campaign(data):
    #Assigns the user forwarded data to use in emailing
    gmail_address = data.get("gmail_address")
    sender_name = data.get("sender_name")
    app_password = data.get("app_password")
    custom_domain = data.get("custom_domain")
    text1 = data.get("text1")
    text2 = data.get("text2")
    subject1 = data.get("subject1")
    subject2 = data.get("subject2")
    send_hour = data.get("send_hour")
    send_minute = data.get("send_minute")
    mail_amount = data.get("mail_amount")
    contacts = data.get("contacts", [])

    sent_list = []
    sent_daily = []
    print(f"The total amount of emails to be sent is: {len(contacts)}")

    while contacts[:]:
        dailyTargets = contacts[:mail_amount]
        dailySentMail = 0
        tomorrowStartTime = datetime.now() + timedelta(hours=24)

        #Cycles through the daily target contacts
        for contact in dailyTargets[:]:
            contactName = contact.get("name")
            contactEmail = contact.get("email")
            contactCountry = contact.get("country")
            contactHas_website = contact.get("hasWebsite")
            contactCountryTimeNow = datetime.now(pytz.timezone(get_timezone_from_country(contactCountry)))

            if contactCountryTimeNow.hour == send_hour and contactCountryTimeNow.minute == send_minute:
                subject = subject1 if contactHas_website else subject2
                body = text1 if contactHas_website else text2
                body = body.format(name=contactName)

                #Sending the mail
                success = send_email(sender_name, contactEmail, subject, body, gmail_address, app_password, custom_domain)
                if success:
                    dailySentMail += 1
                    sent_list.append(contactEmail)
                    sent_daily.append(contactEmail)
                    contacts.remove(contact)

                    campaign_status = {
                        "status": "running",
                        "sent": sent_daily,
                        "total_sent": len(sent_list),
                        "Will_be_running_for": wait_time_str
                    }
                    log_status(campaign_status)
        time.sleep(60) #Checks through the daily targets each minute

        #Calculates how much the loop has to wait to go through the daily batch again
        wait_time = (tomorrowStartTime - datetime.now()).total_seconds()
        hours = int(wait_time) // 3600          #Gets the total hours
        minutes = (int(wait_time) % 3600) // 60 #Gets the total minutes
        wait_time_str = f"{hours} hours and {minutes} minutes"

        campaign_status = {
            "status": "sleeping",
            "sent": sent_daily,
            "total_sent": len(sent_list),
            "next_batch_after": wait_time_str
        }
        log_status(campaign_status)

        print(f"🆗 Daily batch complete. Waiting "+wait_time_str+" to continue the next day.")
        time.sleep(wait_time)
        sent_daily.clear()

    ########################
    campaign_status = {
        "status": "completed",
        "total_sent": sent_list,
    }
    log_status(campaign_status)

@app.route('/send', methods=['POST'])
def start_campaign():
    data = request.get_json()
    total_amount = len(data.get("contacts",[]))
    daily_amount=data.get("mail_amount")
    threading.Thread(target=run_email_campaign, args=(data,)).start()
    return jsonify({
        "status": "started", 
        "mails_to_be_sent" : total_amount,
        "daily_amount": daily_amount,
        "estimated_campaign_time" : f"{total_amount/daily_amount} days",
        "message": "Campaign running in background"
        
    })

@app.route('/campaign-status', methods=['GET'])
def get_campaign_status():
    if not os.path.exists(STATUS_FILE):
        return jsonify({"status": "no campaign started yet"})

    with open(STATUS_FILE, "r") as f:
        return jsonify(json.load(f))

if __name__ == '__main__':
    app.run(port=5000)
