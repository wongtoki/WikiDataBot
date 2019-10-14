import requests 
import json


KEY = 'kLhZweLdy1'
HOST = ' http://robot.tokisbackyard.com'
# HOST = 'http://127.0.0.1:57158'

HEADERS = {
	"Authorization":KEY,
	"Content-Type":"application/json"
}

class Agent:

	def __init__(self, id, lang):
		self.id = id
		self.lang = lang

	#Api call
	#query params: lang(languageCode) & id(sessionid)
	#body {
	# 	query (input from user)
	#	context (a dialogflow feature, I'll explain later.)
	# }

	def ask_json(self, text, context=""):
		host = f'{HOST}/ask?lang={self.lang}&id={self.id}'
		
		body = {
			'query':text,
			'context':context
		}

		res = requests.post(host, json=body, headers=HEADERS)
		return res

	def ask_response_text(self, text):
		res = self.ask_json(text)
		res = json.loads(res.text)["fulfillmentMessages"]
		return res[0]['text']['text'][0]

	def ask_intent(self, text):
		res = self.ask_json(text)
		res = json.loads(res.text)["intent"]
		return res

if __name__ == "__main__":
	agent = Agent()
	agent.ask("Hello")