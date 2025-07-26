import smtplib
import time 
import pycountry
import pytz
from collections import namedtuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Gmail SMTP settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
GMAIL_ADDRESS = "pepsites4u@gmail.com"     # Your actual Gmail account
APP_PASSWORD = "xnfu wioy qgiq pgcl"       # Use an App Password
CUSTOM_DOMAIN_EMAIL = "main@pepsites.org"  # Custom domain email


TARGET_MAIL = ""
TARGET_COUNTRY = ""
HAS_WEBSITE = False
TARGET_NAME = ""
TARGET_TIME_ZONE = ""
BASE1 = 12
BASE2 = 24
MAIL_AMOUNT = 10
text1=""
text2=""
subject1="Want a Free Website Redesign for Your Business?"
subject2="Want a Free Website Design for Your Business?"
MAIL_SUBJECT = ""
MAIL_CONTENT = "Hey there,\n\nI checked out your website for  and love what you’re doing! However I think there’s an opportunity to enhance its design and performance to better attract customers. I’m a web designer, and right now, I’m offering free website redesigns to a few businesses.\n\nI will create a fresh, modern design tailored to your brand—completely free. If you love it, we can discuss how to improve your website further. If not, no worries at all!\n\nWould you be open to a free redesign? Let me know, and I’ll get started right away.\n\n\nBest,\nYiğit\nmain@pepsites.org"
MailTime = namedtuple("MailTime", ["hour", "minute"])
MAIL_TIME = MailTime(6, 37)     #First element is the hour, second is the minute for the email to be sent at the local time


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



def Fake_Email(to_email, subject, body):
    print(f"✅ Sent to {to_email} — {len(dailyTargets)-1} remaining")

def get_default_timezone(country_name):
    try:
        country = pycountry.countries.get(name=country_name)
        if not country:
            return "UTC"
        timezones = pytz.country_timezones.get(country.alpha_2)
        if timezones:
            return timezones[0]  # usually the most common or capital-based
    except:
        pass
    return "UTC"


#Reading all lines from the sorted list
with open(r"C:\Users\ygtyi\Desktop\Code\emailer\ContactsWorkspace.txt", "r", encoding="utf-8", errors="replace") as file:
    lines = file.readlines()

#Assigns the blacklisted targets from source text file
with open(r"C:\Users\ygtyi\Desktop\Code\emailer\ContactsBlacklist.txt", "r", encoding="utf-8", errors="replace") as file:
    blacklistedTargets = file.readlines()

#Defines the email content for the businesses that have a website
for i in range(BASE1):
    text1 = text1 + lines[i]

#Defines the email content for the businesses that DO NOT have a website
for i in range(BASE1,BASE2):
    text2 = text2 + lines[i]

dailyTargets = lines[BASE2:BASE2+MAIL_AMOUNT]       # Assigns the daily targets from the list
del lines[BASE2:BASE2+MAIL_AMOUNT]                  # Then removes them from the source


#MAILER LOOP 
while dailyTargets:
    for target in dailyTargets[:]:
        HAS_WEBSITE = True
        nameIndex = target.find("Name:")
        emailIndex = target.find("E-mail:", nameIndex+5)
        countryIndex = target.find("Country:", emailIndex+5)
        websiteIndex = target.find("Website:", countryIndex+3)
        if websiteIndex==-1:
            websiteIndex = target.find("No web", countryIndex+3)
            HAS_WEBSITE = False

        TARGET_NAME = target[nameIndex+6:emailIndex-2]
        if TARGET_NAME.endswith(" "): TARGET_NAME = TARGET_NAME[:-1]
        TARGET_MAIL= target[emailIndex+8:countryIndex-2]
        TARGET_COUNTRY = target[countryIndex+9:websiteIndex-2]
        if HAS_WEBSITE:
            MAIL_CONTENT = text1.format(name=TARGET_NAME)
            MAIL_SUBJECT = subject1
        else:
            MAIL_CONTENT = text2.format(name=TARGET_NAME)
            MAIL_SUBJECT = subject2

        TARGET_TIME_ZONE = get_default_timezone(TARGET_COUNTRY)

        if TARGET_MAIL in blacklistedTargets:
            continue

        now = datetime.now(pytz.timezone(TARGET_TIME_ZONE))      # Gets the current time of the selected business according to its timezone
        print("Business Name: "+ TARGET_NAME + ", Country: " + TARGET_COUNTRY + ", Email: "+ TARGET_MAIL+ ", Current Time: " + ("0" if now.hour<10 else "") + str(now.hour) + "." + ("0" if now.minute<10 else "")+ str(now.minute))

        if now.hour == MAIL_TIME.hour and now.minute == MAIL_TIME.minute:
            Fake_Email(TARGET_MAIL,MAIL_SUBJECT, MAIL_CONTENT)   # Sends the email
            blacklistedTargets.append(TARGET_MAIL)               # Blacklists the email address
            dailyTargets.remove(target)                          # Remove from the daily list

    time.sleep(60)  # Check every minute
    
    
with open(r"C:\Users\ygtyi\Desktop\Code\emailer\ContactsWorkspace.txt", "w", encoding="utf-8", errors="replace") as file:
    for line in lines:
        file.write(line)

with open(r"C:\Users\ygtyi\Desktop\Code\emailer\ContactsBlacklist.txt", "w", encoding="utf-8", errors="replace") as file:
    for line in blacklistedTargets:
        file.write(line + "\n")


    

# Example usage
#send_email(TARGET_MAIL, MAIL_SUBJECT, MAIL_CONTENT)
