from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from wikidata.sparql.sparql import Courier

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

            # if 'post_selected_movie' in request.POST:
            #     print('the q-number', request.POST['post_selected_movie'])
            #
            if 'post_search' in request.POST:
                # initialise form for validation with POST data
                form = dialogForm(data={'search': request.POST['post_search']})
            else:
                form = dialogForm(data={'search': 'test'})

            if form.is_valid() and 'post_search' in request.POST:

                return search_for_movie(request)
            #
            # elif form.is_valid() and 'post_entity' in request.POST:
            #
            #     entity = request.POST.get('post_entity')
            #     entity_title = request.POST.get('post_entity_title')
            #     response = 'Responding with the answer'
            #
            #     ## return to user-interface
            #     dialog = render_to_string('wikidata_2selected.html', {'question': entity_title, 'response': response, 'q_number': entity})
            #     res = {'response': dialog}
            #     return HttpResponse(json.dumps(res), 'application/json')
            #
            else:
                # search_in_list(form)
                print("TODO")
                return

def search_in_list(form):
    print('form is not valid')
    print(form.errors)
    print(form.non_field_errors)


def search_for_movie(request):
    search_question = request.POST.get('post_search')

    # store the question in the session
    # request.session['question'] = search_question

    print('This is the search question: ', search_question)

    ## Google Dialogflow
    dialog_flow_agent = Agent()
    json_resp = dialog_flow_agent.ask_json(search_question, sessionId=create_random_string())
    # return "nothing here"

    parsed = json.loads(json_resp.text)
    # print('parsed: ', parsed)
    courier = Courier()
    result = courier.deliver(parsed)
    print('delivery: ', result[1])
    #     # intent = agent.ask_intent(search, sessionId=random_string)
    #     # print(intent)
    #     info = json_resp.json()['parameters']['fields']
    #     # movie = info['movie_name']['stringValue']
    #     # property = info['object_properties']['stringValue']
    #
    #     if data['results']:
    #         for item in data['results']['bindings']:
    #             identifier = item['item']['value'].split('/')[-1]
    #             title = item['itemLabel']['value']
    #             date = item['year']['value']
    #             # convert JSON timestamp to Python date object
    #             date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%fZ')
    #
    #             # fill dictionary
    #             info[identifier] = {'title': title, 'year': date.year, 'genre': []}
    #
    #         # append genre to list
    #         for item in data['results']['bindings']:
    #             identifier = item['item']['value'].split('/')[-1]
    #             genre = item['genreLabel']['value']
    #             info[identifier]['genre'].append(genre)
    #
    #     # check if there are multiple results
    #     if len(info.keys()) > 1:
    #         options = info
    #     else:
    #         options = ''

    # Displaying of the answer.
    if (result[0]):
        dialog = render_to_string('wikidata_2selected.html', {
            'question': search_question,
            'response': ', '.join(result[1]),
            'disambiguation': result
        })
    else:
        response = 'Which of the following movies?'
        dialog = render_to_string('wikidata_1selections.html', {
            'question': search_question,
            'response': response,
            'disambiguation': result,
        })
    res = {'response': dialog}
    return HttpResponse(json.dumps(res), 'application/json')


def create_random_string():
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return random_string