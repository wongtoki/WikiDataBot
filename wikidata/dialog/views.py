from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from wikidata.sparql.sparql import Courier
from wikidata.dialogflow.dialogflow import Agent

import json
import random
import string
from collections import OrderedDict
from operator import getitem

# import models

# import forms
from dialog.forms import dialogForm


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

                # the returned dialog in HTML-format
                dialog = return_response(request)

            elif 'post_entity_title' in request.POST:
                '''The user made a dropdown selection'''

                intent_value = request.POST.getlist('post_entity[]')
                movie_title = request.POST['post_entity_title']
                movie_href = request.POST['post_entity_link']

                '''for debugging
                print('intent_value', intent_value)
                print(type(intent_value))
                print(intent_value[0])
                '''

                if intent_value[0]:
                    '''A movie was selected by the user'''

                    # what HTML to return to user interface
                    dialog = render_to_string('returns/dropdown_selection_made.html',
                                              {'question': movie_title, 'response': intent_value, 'link': movie_href})

                else:
                    '''User selected the 'other' option in the dropdown-select'''

                    bot_resp = [['Please specify which movie a bit better.']]

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
    json_resp = agent.ask_json(user_input, sessionId=create_random_string())

    parsed = json.loads(json_resp.text)
    boolean, bot_resp = courier.deliver(parsed)

    '''for debugging
    print('bot_resp')
    print(bot_resp)'''

    if boolean:
        '''Response is a lists of lists, with either ['string'] or [answer, link]'''

        if bot_resp[0][0] == '':
            '''Response is non-valid, Courier delivered an empty string'''
            print('There is an empty response from the Courier..')

            responses = [
                "Sorry, I did not get that.",
                "Could you repeat that?",
                "I did not understand, can you repeat?",
                "I don't understand that.",
                "Sorry, could you say that again?"
            ]

            # returning a response in the correct format
            bot_resp = [[random.choice(responses)]]

        # what HTML to return to user interface
        dialog = render_to_string('returns/normal_response.html',
                                  {'question': user_input, 'response': bot_resp})

    else:
        '''A dropdown select with movie choices should be returned'''

        if bot_resp:
            '''Response is valid'''

            response_question = 'Please select the correct movie.'

            # this orders the movies by year
            ordered = OrderedDict(sorted(bot_resp.items(),
                                         key=lambda x: getitem(x[1], 'year')))

            # what HTML to return to user interface
            dialog = render_to_string('returns/dropdown_select.html', {'question': user_input, 'response': response_question, 'selections': ordered})

        else:
            '''Response is an empty dictionary (for instance: no movies were found)'''

            # returning a response in the correct format
            bot_resp = [['I could not find any movie with that name.']]

            # what HTML to return to user interface
            dialog = render_to_string('returns/normal_response.html',
                                      {'question': user_input, 'response': bot_resp})

    return dialog


def create_random_string():
    '''creates a random string for Dialogflow Agent'''
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return random_string
