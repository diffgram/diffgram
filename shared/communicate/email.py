# OPENCORE - ADD
import requests
from shared.settings import settings
import smtplib

from email.mime.text import MIMEText


class Communicate_Via_Email():

    def __init__(self):
        self.domain_name = settings.EMAIL_DOMAIN_NAME
        self.api_key = settings.MAILGUN_KEY
        self.reply_to = settings.EMAIL_REPLY_TO
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_pass = settings.SMTP_PASSWORD

    def send(self, email: str, subject: str, message: str, email_list: list = []):
        recipients = email_list
        if len(email_list) == 0:
            recipients = [email]
        s = smtplib.SMTP(self.smtp_host, self.smtp_port)
        s.ehlo()
        s.starttls()
        for from_email in recipients:
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = f"Diffgram <web@{self.domain_name}>"
            msg['To'] = from_email

            s.login('postmaster@mail.diffgram.com', self.smtp_pass)
            s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.quit()

    def send_legacy(self, email, subject, message, email_list = [], html = None):
        data = {"from": f"Diffgram <web@{self.domain_name}>",
                "to": [str(email)] if len(email_list) == 0 else [str(email) for email in
                                                                 email_list],
                "subject": str(subject),
                "text": str(message),
                "h:Reply-To": self.reply_to,
                }

        if html:
            data['html'] = str(html)

        result = requests.post(f"https://api.mailgun.net/v3/{self.domain_name}/messages",
                               auth = ("api", self.api_key),
                               data = data
                               )

        return result


communicate_via_email = Communicate_Via_Email()

# future naming idea: Comms.Email.send() or something?
