# OPENCORE - ADD
import requests
from shared.settings import settings



class Communicate_Via_Email():

	def __init__(self):
		self.domain_name = settings.EMAIL_DOMAIN_NAME
		self.api_key = settings.MAILGUN_KEY

	def send(self, email, subject, message, email_list=[]):

		return requests.post("https://api.mailgun.net/v3/" + self.domain_name + "/messages",
			auth=("api", self.api_key),
			data={"from": "Diffgram <web@" + self.domain_name + ">",
					"to": [str(email)] if len(email_list) == 0 else [str(email) for email in email_list],
					"subject": str(subject),
					"text": str(message),
					"h:Reply-To": "change_me@yourdomain_change_me.com"
				}
			)

communicate_via_email = Communicate_Via_Email()

# future naming idea: Comms.Email.send() or something?
