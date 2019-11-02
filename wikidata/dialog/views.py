from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from wikidata.sparql.sparql import Courier
from wikidata.dialogflow.dialogflow import Agent

import json
import random
import string

# import models

# import forms
from dialog.forms import dialogForm


def create_random_string():
    '''A function to return a random string used for the Agent'''
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return random_string

# Create your views here.
def index(request):
    '''This is what is displayed on the normal page'''
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
            print('request information:', request.POST)

            if 'post_search' in request.POST:
                '''A question has been asked'''

                # the returned response in HTML in a dictionary
                res = return_response(request)

            elif 'post_entity_title' in request.POST:
                '''The user made a dropdown selection'''

                intent_value = request.POST['post_entity']
                movie_title = request.POST['post_entity_title']

                if intent_value:
                    '''A movie was selected by the user'''

                    # what HTML to return to user interface
                    dialog = render_to_string('returns/normal_response.html',
                                              {'question': movie_title, 'response': intent_value})
                    res = {'response': dialog}

                else:
                    '''User selected the 'other' option in the dropdown-select'''

                    bot_resp = 'Please specify which movie a bit better.'
                    # what HTML to return to user interface
                    dialog = render_to_string('returns/normal_response.html',
                                              {'question': movie_title, 'response': bot_resp})
                    res = {'response': dialog}

            return HttpResponse(json.dumps(res), 'application/json')


def return_response(form):
    '''This takes the POST values form the request and returns either a dropdown or string response'''

    # Google Dialogflow class
    agent = Agent()
    # SPARQL query and response class
    courier = Courier()

    user_input = form.POST['post_search']
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    json_resp = agent.ask_json(user_input, sessionId=random_string)

    parsed = json.loads(json_resp.text)
    boolean, bot_resp = courier.deliver(parsed)

    '''for debugging!'''
    boolean = False
    bot_resp = [['Avatar', '2008', 'James'], ['Avatar the series', '2001', 'director_name']]

    print(bot_resp)

    if boolean:
        '''The string response from DialogFlow should be returned'''

        # bot_resp is always a list, with in this case the string in it
        # TODO: if there's more responses it returns multiple list items.. which then need to be concatenated here
        # TODO: should be done in the actual output of courier.deliver()
        # TODO: for now this is an easy fix
        if len(bot_resp) == 1:
            textual_response = bot_resp[0]
        else:
            textual_response = ' and '.join(bot_resp)
            print(textual_response)

        # what HTML to return to user interface
        dialog = render_to_string('returns/normal_response.html', {'question': user_input, 'response': textual_response})

    else:
        '''A dropdown select with movie choices should be returned'''

        response_question = 'Which of the following movies?'

        # what HTML to return to user interface
        dialog = render_to_string('returns/dropdown_select.html', {'question': user_input, 'response': response_question, 'selections': bot_resp})

    response = {'response': dialog}

    return response


