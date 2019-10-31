import requests
import json

# requirements for Dialogflow agent
KEY = 'kLhZweLdy1'
HOST = 'https://robot.tokisbackyard.com'
HEADERS = {
    "Authorization": KEY,
    "Content-Type": "application/json"
}

class Agent:
    def __init__(self):
        pass

    def ask_json(self, text, lang='en', sessionId='test', context=""):
        host = f'{HOST}/ask?lang={lang}&id={sessionId}'

        body = {
            'query': text,
            'context': context
        }

        res = requests.post(host, json=body, headers=HEADERS)
        return res

    def ask_response_text(self, text, lang='en', sessionId='test'):
        res = self.ask_json(text, lang, sessionId)
        res = json.loads(res.text)["fulfillmentMessages"]
        return res[0]['text']['text'][0]

    def ask_intent(self, text, lang='en', sessionId='test'):
        res = self.ask_json(text, lang, sessionId)
        res = json.loads(res.text)["intent"]
        return res

