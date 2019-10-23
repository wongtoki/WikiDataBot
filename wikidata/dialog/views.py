from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

import requests
import json
import random
import string
import datetime

# import models

# import forms
from dialog.forms import dialogForm

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
    # 	query (input from user)
    #	context (a dialogflow feature, I'll explain later.)
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



# Create your views here.
def index(request):
    assert isinstance(request, HttpRequest)

    form = dialogForm(auto_id=False)

    context = {
        'title': 'Question-answering bot with DialogFlow and Wikidata',
        'tags': ['tag1', 'tag2', 'tag3', 'tag4', 'tag5'],
        'author': 'Gaetana Ruggiero, Toki Wong, Ana Roman, Louis de Bruijn',
        'date': 'Oct 8, 2019',
        'form': form,
    }
    return render(request, 'index.html', context)

@csrf_exempt
def wikidata_dialog(request):
    '''catches AJAX POST and returns response'''
    if request.is_ajax():
        if request.method == 'POST':
            print(request.POST)

            if 'post_search' in request.POST:
                # initialise form for validation with POST data
                form = dialogForm(data={'search': request.POST['post_search']})
            else:
                # TODO: initalise new form hereeeee !!
                form = dialogForm(data={'search': 'test'})

            if form.is_valid() and 'post_search' in request.POST:

                search = request.POST.get('post_search')

                random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                print('random_string', random_string)

                ## Google Dialogflow
                agent = Agent()

                # response = agent.ask_response_text(search, sessionId=random_string)
                json_resp = agent.ask_json(search, sessionId=random_string)
                print(json_resp)
                # intent = agent.ask_intent(search, sessionId=random_string)
                # print(intent)
                info = json_resp.json()['parameters']['fields']
                # movie = info['movie_name']['stringValue']
                # property = info['object_properties']['stringValue']

                ## if there is no movie
                ## return the fulfillmentText
                # print(movie, property)
                movie = 'Avatar'

                query = '''
                    SELECT ?item ?itemLabel ?genreLabel ?year
                    WHERE
                    {
                      ?item wdt:P31/wdt:P279* wd:Q2431196 .
                      ?item wdt:P1476 ?title .
                      ?item wdt:P577 ?year .
                      ?item wdt:P136 ?genre .
                      FILTER contains(?title,"%s")
                      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
                    }
                ''' % (movie)

                # create the request
                data = requests.get('https://query.wikidata.org/sparql',
                                    params={'query': query, 'format': 'json'}).json()

                info = {}

                if data['results']:
                    for item in data['results']['bindings']:
                        identifier = item['item']['value'].split('/')[-1]
                        title = item['itemLabel']['value']
                        date = item['year']['value']
                        # convert JSON timestamp to Python date object
                        date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%fZ')

                        # fill dictionary
                        info[identifier] = {'title': title, 'year': date.year, 'genre': []}

                    # append genre to list
                    for item in data['results']['bindings']:
                        identifier = item['item']['value'].split('/')[-1]
                        genre = item['genreLabel']['value']
                        info[identifier]['genre'].append(genre)

                # check if there are multiple results
                if len(info.keys()) > 1:
                    options = info
                else:
                    options = ''

                response = 'Which of the following movies?'

                ## return to user-interface
                dialog = render_to_string('wikidata_dialog.html', {'question': search, 'response': response, 'disambiguation': options})
                res = {'response': dialog}
                return HttpResponse(json.dumps(res), 'application/json')

            elif form.is_valid() and 'post_entity' in request.POST:

                entity = request.POST.get('post_entity')
                entity_title = request.POST.get('post_entity_title')
                response = 'Responding with the answer'

                ## return to user-interface
                dialog = render_to_string('wikidata_dialog.html', {'question': entity_title, 'response': response, 'disambiguation': ''})
                res = {'response': dialog}
                return HttpResponse(json.dumps(res), 'application/json')

            else:
                print('form is not valid')
                print(form.errors)
                print(form.non_field_errors)

    else:
        print('WAT DU FUCK')