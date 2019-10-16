#!/usr/bin/env python3
# File name: wikidata_qa_flow.py
# Description: Using the DialogFlow and Wikidata to emulate workflow
# Author: Louis de Bruijn
# Date: 14-10-2018

import requests
import json
import random
import string

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

    # Api call
    # query params: lang(languageCode) & id(sessionid)
    # body {
    #   query (input from user)
    #   context (a dialogflow feature, I'll explain later.)
    # }

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


def create_query(subject, prop):
    query ='''SELECT DISTINCT ?itemLabel WHERE { wd:%s wdt:%s ?item.
        SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
        ''' % (subject, prop)
    return query


def fetch_api(search_term, type_value):
    # wikidata API
    url = 'https://www.wikidata.org/w/api.php'
    params = {'action': 'wbsearchentities',
        'language': 'en',
        'format': 'json'}
    # create type parameter
    params['type'] = type_value
    # create search term parameter
    params['search'] = search_term
    # call API
    json = requests.get(url, params).json()
    # fetch results
    if json['search']:
        return [result['id'] for result in json['search']]
    else:
        return []


def main():

    search = 'Who is the director of Avatar (2009)?'
    search = 'Who is the director of Avatar?'

    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    agent = Agent()
    # response = agent.ask_response_text(search, sessionId=random_string)
    json_resp = agent.ask_json(search, sessionId=random_string)
    # intent = agent.ask_intent(search, sessionId=random_string)

    info = json_resp.json()['parameters']['fields']
    movie = info['movie_name']['stringValue']
    prop = info['object_properties']['stringValue']

    print(movie, prop)

    movie_id = fetch_api(movie, 'item')
    print(movie_id)

if __name__ == '__main__':
    main()
