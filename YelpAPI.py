import io
import json
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator

class yelp(object):

	def __init__(self, input):
		with io.open('./config.json') as cred:
			creds = json.load(cred)
			auth = Oauth1Authenticator(**creds)
			client = Client(auth)
		try:
			self.response = client.get_business(input)
		except:
			print 'No results found.'

	def get_url(self):
		return self.response.business.url

	def get_review_number(self):
		return self.response.business.review_count

	def get_overall_rate(self):
		return self.response.business.rating

	def get_categories(self):
		return self.response.categories