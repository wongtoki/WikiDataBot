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
            sparql = SPARQLWrapper(endpoint_url)
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            print(results)
        except:
            print ("The wikidata endpoint is not answering")
            return

        value = results['results']
        if (value):
            return value
        else:
            print("\n query didnt work")
            return

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

        # Using a dictionary for easy intent response
        packages = {
            "ask_oscar_winner": ask_oscar_winner,
            "ask_oscar_winner_movie": ask_oscar_winner_movie,
            "ask_release_date": ask_release_date,
            "ask_oscar_winner_director": ask_oscar_winner_director
        }

        # Calling the function assigned to the dictionary key
        try:
            sparql_result = packages[intent_name](response)

            if (sparql_result[0] == False):
                return [True, [default_response]]
        except:
            return [True, [default_response]]

        return sparql_result

    # Wrapping the params
    def __get_year(self, response):
        year_string = response["parameters"]["fields"]["date-period"]["structValue"]["fields"]["endDate"]["stringValue"]
        year = year_string[:4]
        return year

    def __get_movie_name(self, response):
        movie_string = response["parameters"]["fields"]["movie_name"]["stringValue"]
        return movie_string

    # Return the movie that won the Oscar in a given year
    def __query_oscar_movies(self, response):
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

        return [
            True,
            [
                [
                    res['bindings'][0]['movieLabel']['value'],  # the movie name
                    res['bindings'][0]['movie']['value']  # the Wikidata link
                ]
            ]
        ]

    # Return the Oscar winners for a given year
    # Will return an array containing both male and female
    # eg ['Rami Malek', 'Olivia Colman']
    def __query_oscar_winner(self, response):
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
            return [True, ["The Wikidata endpoint isnt answering."]]

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

    def __query_movie_release_date(self, response):
        movie = self.__get_movie_name(response)
        query = """
            SELECT ?item ?itemLabel ?year
            WHERE
            {
            ?item wdt:P31/wdt:P279* wd:Q11424 .
            ?item wdt:P1476 ?title .
            ?item wdt:P577 ?year .
            FILTER contains(lcase(str(?title)),"%s")
            SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
            }
        """ % (movie.lower())

        res = self.__send_query(query)

        results = [False,[]] # I am not sure about this line.
        for v in res["bindings"]:
            # convert year to Python dateobject
            date = convert_date(v["year"]["value"])

            output = {
                "moviename": v["itemLabel"]["value"],
                "year": date.year
            }
            results[1].append(output)

        return results

    def __query_oscar_winner_director(self, response):
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

    def __query_genre(self, response):
        movie = self.__get_movie_name(response)

        query = """
            SELECT ?item ?itemLabel ?genreLabel
            WHERE
            {
            ?item wdt:P31/wdt:P279* wd:Q11424 .
            ?item wdt:P1476 ?title .
            ?item wdt:P136 ?genre .
            FILTER contains(lcase(str(?title)),"%s")
            SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
            }
        """ % (movie.lower())

        res = self.__send_query(query)
        res = res["bindings"][0]
        return [False, res] #Change this line

    def __query_duration(self, response):
        movie = self.__get_movie_name(response)

        query = """
            SELECT ?item ?itemLabel ?duration
            WHERE
            {
            ?item wdt:P31/wdt:P279* wd:Q11424 .
            ?item wdt:P1476 ?title .
            ?item wdt:P2047 ?duration .
            FILTER contains(lcase(str(?title)),"%s")
            SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
            }
        """ % (movie.lower())

        res = self.__send_query(query)
        res = res["bindings"][0]
        return [False, res] #Change this line

    def __query_cast(self, response):
        movie = self.__get_movie_name(response)
        query = """
            SELECT ?item ?itemLabel ?castLabel
            WHERE
            {
            ?item wdt:P31/wdt:P279* wd:Q11424 .
            ?item wdt:P1476 ?title .
            ?item wdt:P161 ?cast .
            FILTER contains(lcase(str(?title)),"%s")
            SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
            }
        """ % (movie.lower())
        res = self.__send_query(query)
        res = res["bindings"][0]
        return [False, res] #Change this line

def convert_date(sparql_timestamp):
    '''convert JSON timestamp to Python date object'''
    return datetime.datetime.strptime(sparql_timestamp, '%Y-%m-%dT%H:%M:%S%fZ')


if __name__ == "__main__":
    courior = Courier()

    delivery = courior.deliver()
    print(delivery)
    # print(courior.query_oscar_winner_actor(2019))
