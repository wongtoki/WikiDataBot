import requests
from datetime import datetime
import json
import urllib.parse as encodeurl
from SPARQLWrapper import SPARQLWrapper, JSON
import datetime

class Courier:

    def __init__(self):
        pass

    # Communicates with the wikidata endpoint.
    def __send_query(self, query):
        endpoint_url = "https://query.wikidata.org/sparql"

        try:
            # create the request

            params = f"?format=json&query={encodeurl.quote(query)}"

            results = requests.get(endpoint_url+params).json()

            '''Sparql wrapper
            sparql = SPARQLWrapper(endpoint_url)
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            '''

        except Exception as e:
            # TODO: we sould try to run it in 5 seconds again, see if it works then :D
            print ("The wikidata endpoint is not answering")
            print(e)
            return 'The Wikidata endpoint is not responding.'

        value = results['results']
        if value['bindings']:
            return value
        else:
            print("\n query didnt work")
            return 'Unfortunately, this information is not on Wikidata.'


    def deliver(self, response):
        # gets the intent name + default response from the DF response.
        intent_name = response["intent"]["displayName"]
        default_response = response["fulfillmentText"]

        print("intent name: ", intent_name)

        # Assign function names to variables so they won't be called during assignment
        ask_oscar_winner_movie = self.__query_oscar_movies
        ask_oscar_winner = self.__query_oscar_winner
        ask_release_date = self.__query_movie_release_date
        ask_oscar_winner_director = self.__query_oscar_winner_director
        ask_director = self.__query_director
        ask_duration = self.__query_duration
        ask_genre = self.__query_genre
        ask_cast = self.__query_cast

        # Using a dictionary for easy intent response
        packages = {
            "ask_oscar_winner": ask_oscar_winner,
            "ask_oscar_winner_movie": ask_oscar_winner_movie,
            "ask_release_date": ask_release_date,
            "ask_oscar_winner_director": ask_oscar_winner_director,
            "ask_director": ask_director,
            "ask_duration": ask_duration,
            "ask_genre": ask_genre,
            "ask_cast": ask_cast
        }

        # Calling the function assigned to the dictionary key
        try:
            sparql_result = packages[intent_name](response)
        except Exception as e:
            print('error in calling the assigned sparql_result:', e)

            # this is a list of lists, which is the same format as all the other answers, for HTML front-end looping
            return [True, [[default_response]]]

        return sparql_result

    # Wrapping the params
    def __get_year(self, response):
        year_string = response["parameters"]["fields"]["date-period"]["structValue"]["fields"]["endDate"]["stringValue"]
        year = year_string[:4]
        return year

    def __get_movie_name(self, response):
        movie_string = response["parameters"]["fields"]["movie_name"]["stringValue"]
        return movie_string


    def __query_oscar_movies(self, response):
        '''Return the movie that won the Oscar in a given year'''
        year = self.__get_year(response)

        query = """
            SELECT ?movie ?movieLabel ?date 
            WHERE
            {
            ?movie p:P166 ?awardstatement .
            ?movie wdt:P31 wd:Q11424 .
            ?awardstatement ps:P166 wd:Q102427  .
            ?awardstatement pq:P585 ?date .
            FILTER((?date >= "%s-01-01T00:00:00Z"^^xsd:dateTime) && (?date <= "%s-12-31T00:00:00Z"^^xsd:dateTime))
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en,fr" . }
            }
        """ % (year, year)

        res = self.__send_query(query)
        if isinstance(res, dict):
            return [
                True,
                [
                    [
                        res['bindings'][0]['movieLabel']['value'],  # the movie name
                        res['bindings'][0]['movie']['value']  # the Wikidata link
                    ]
                ]
            ]
        else:
            return [True, [[res]]]



    def __query_oscar_winner(self, response):
        '''Return the Oscar winners for a given year'''
        year = self.__get_year(response)

        query_male_actor = """
            SELECT ?actor ?actorLabel ?date ?forWork ?forWorkLabel
            WHERE
            {
            ?actor wdt:P31 wd:Q5 .
            ?actor p:P166 ?awardstatement .
            ?awardstatement ps:P166 wd:Q103916 .
            ?awardstatement pq:P585 ?date .
            ?awardstatement pq:P1686 ?forWork .
            FILTER((?date >= "%s-01-01T00:00:00Z"^^xsd:dateTime) && (?date <= "%s-12-31T00:00:00Z"^^xsd:dateTime))
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en,fr" . }
            }
        """ % (year, year)

        query_female_actor = """
            SELECT ?actor ?actorLabel ?date ?forWork ?forWorkLabel
            WHERE
            {
            # find a human
            ?actor wdt:P31 wd:Q5 .
            ?actor p:P166 ?awardstatement .
            ?awardstatement ps:P166 wd:Q103618 .
            ?awardstatement pq:P585 ?date .
            ?awardstatement pq:P1686 ?forWork .
            FILTER((?date >= "%s-01-01T00:00:00Z"^^xsd:dateTime) && (?date <= "%s-12-31T00:00:00Z"^^xsd:dateTime))
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en,fr" . }
            }
        """ % (year, year)

        try:
            res1 = self.__send_query(query_male_actor)
            res2 = self.__send_query(query_female_actor)
        except:
            if res1:
                return [True, [[res1]]]
            elif res2:
                return [True, [[res2]]]

        return [
            True,
            [
                [
                    res1['bindings'][0]['actorLabel']['value'], # the actor name
                    res1['bindings'][0]['actor']['value'] # the Wikidata link
                ],
                [
                    res2['bindings'][0]['actorLabel']['value'], # the actress name
                    res2['bindings'][0]['actor']['value'] # the Wikidata link
                ]
            ]
        ]


    def __query_oscar_winner_director(self, response):
        '''Return the Oscar winning director for a given year'''
        year = self.__get_year(response)
        query = """
            SELECT ?actor ?actorLabel ?date ?forWork ?forWorkLabel
            WHERE
            {
            # find a human
            ?actor wdt:P31 wd:Q5 .
            # Now comes the statements/qualifiers magic:
            ?actor p:P166 ?awardstatement .
            ?awardstatement ps:P166 wd:Q103360 .
            ?awardstatement pq:P585 ?date .
            ?awardstatement pq:P1686 ?forWork .
            FILTER((?date >= "%s-01-01T00:00:00Z"^^xsd:dateTime) && (?date <= "%s-12-31T00:00:00Z"^^xsd:dateTime))
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en,fr" . }
            }
        """ % (year, year)
        res = self.__send_query(query)
        if isinstance(res, dict):
            res = res["bindings"][0]

            return [
                True,
                [
                    [
                        res["actorLabel"]["value"],  # the director's name
                        res["actor"]["value"]  # the Wikidata link
                    ]
                ]
            ]
        else:
            return [True, [[res]]]


    def __query_movie_release_date(self, response):
        '''Return the release date for a given movie'''
        movie = self.__get_movie_name(response)
        query = """
            SELECT ?item ?itemLabel ?year
            WHERE
            {
            ?item wdt:P31/wdt:P279* wd:Q2431196 .
            ?item wdt:P1476 ?title .
            ?item wdt:P577 ?year .
            FILTER contains(lcase(str(?title)),"%s") .
            SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
            }
        """ % (movie.lower())

        res = self.__send_query(query)
        if isinstance(res, dict):
            # contains a dictionary with all the movie information
            movies = movie_answer(res, 'year')

            return [False, movies]

        else:
            return [True, [[res]]]


    def __query_duration(self, response):
        '''Return the duration for a given movie'''
        movie = self.__get_movie_name(response)

        query = """
            SELECT ?item ?itemLabel ?duration ?year
            WHERE
            {
            ?item wdt:P31/wdt:P279* wd:Q2431196 .
            ?item wdt:P1476 ?title .
            ?item wdt:P2047 ?duration .
            ?item wdt:P577 ?year .
            FILTER contains(lcase(str(?title)),"%s") .
            SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
            }
        """ % (movie.lower())

        res = self.__send_query(query)
        if isinstance(res, dict):
            # contains a dictionary with all the movie information
            movies = movie_answer(res, 'duration')

            return [False, movies]

        else:
            return [True, [[res]]]


    def __query_genre(self, response):
        '''Return the genre for a given movie'''
        movie = self.__get_movie_name(response)

        query = """
            SELECT ?item ?itemLabel ?genreLabel ?year
            WHERE
            {
            ?item wdt:P31/wdt:P279* wd:Q2431196 .
            ?item wdt:P1476 ?title .
            ?item wdt:P136 ?genre .
            ?item wdt:P577 ?year .
            FILTER contains(lcase(str(?title)),"%s") .
            SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
            }
        """ % (movie.lower())

        res = self.__send_query(query)
        if isinstance(res, dict):
            # contains a dictionary with all the movie information
            movies = movie_answer(res, 'genreLabel')

            return [False, movies]

        else:
            return [True, [[res]]]


    def __query_cast(self, response):
        '''Return the cast for a given movie'''
        movie = self.__get_movie_name(response)
        query = """
            SELECT ?item ?itemLabel ?castLabel ?year
            WHERE
            {
            ?item wdt:P31/wdt:P279* wd:Q2431196 .
            ?item wdt:P1476 ?title .
            ?item wdt:P161 ?cast .
            ?item wdt:P577 ?year .
            FILTER contains(lcase(str(?title)),"%s") .
            SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
            }
        """ % (movie.lower())
        res = self.__send_query(query)
        if isinstance(res, dict):
            # contains a dictionary with all the movie information
            movies = movie_answer(res, 'castLabel')

            return [False, movies]

        else:
            return [True, [[res]]]



    def __query_director(self, response):
        '''Return the director for a given movie'''
        movie = self.__get_movie_name(response)
        query = """
            SELECT ?item ?itemLabel ?directorLabel ?year
            WHERE
            {
            ?item wdt:P31/wdt:P279* wd:Q2431196 .
            ?item wdt:P1476 ?title .
            ?item wdt:P57 ?director .
            ?item wdt:P577 ?year .
            FILTER contains(lcase(str(?title)),"%s")
            SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
            }
        """ % (movie.lower())
        res = self.__send_query(query)
        if isinstance(res, dict):
            # contains a dictionary with all the movie information
            movies = movie_answer(res, 'directorLabel')

            return [False, movies]

        else:
            return [True, [[res]]]


def convert_date(sparql_timestamp):
    '''convert JSON timestamp to Python date object'''
    return datetime.datetime.strptime(sparql_timestamp, '%Y-%m-%dT%H:%M:%S%fZ')


def movie_answer(res, label):
    '''returns a dictionary with all necessary information for HTML dropdown-select'''

    movies = {}
    for movie in res["bindings"]:
        '''collect all the static values we need per movie'''
        link = movie['item']['value']
        q_number = link.split('/')[-1]
        name = movie['itemLabel']['value']
        date = convert_date(movie["year"]["value"])

        # fill a dictionary w/ q_number as identifier with movie information
        movies[q_number] = {'title': name, 'year': date.year, 'href': link, 'answer': set(), 'answer_string': ''}

    for movie in res["bindings"]:
        '''collect the actual answer in a list, because it might be > 1'''
        # get the identifier (q_number)
        link = movie['item']['value']
        q_number = link.split('/')[-1]
        answer = movie[label]['value']

        if label == "year":
            '''exception for query_movie_release_date, because the answer is the date'''
            date = convert_date(answer)
            answer = date.strftime("%A %d %B, %Y")

        elif label == "duration":
            '''exception for duration, to append "minutes" after the answer'''
            answer = answer + ' minutes'

        # append the answer to the set in the dictionary
        # using a set, because the answers have to be unique
        movies[q_number]['answer'].add(answer)

    for key, value in movies.items():
        '''convert the set with answers to a pipe-delimited string in order to convert to JS array'''
        movies[key]['answer_string'] = '|'.join(movies[key]['answer'])


    '''append a nice natural-language string in the front-end'''
    nl_strings = {
        "year": ' was released on',
        "duration": ' lasts for',
        "genreLabel": ["'s genre is", "'s genres are"],
        "castLabel": ["'s cast is", "'s cast are"],
        "directorLabel": "'s director is",
     }
    for key, value in movies.items():
        if label == "genreLabel" or label == 'castLabel':
            if len(movies[key]['answer']) > 1:
                movies[key]['nl_string'] = nl_strings[label][1]
            else:
                movies[key]['nl_string'] = nl_strings[label][0]
        else:
            movies[key]['nl_string'] = nl_strings[label]

    return movies


if __name__ == "__main__":
    courior = Courier()

    delivery = courior.deliver()
    # print(delivery)
    # print(courior.query_oscar_winner_actor(2019))
