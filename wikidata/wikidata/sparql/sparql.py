import requests
from datetime import datetime
import json
import urllib.parse as encodeurl

class Courier:
    # This class is used as a universal parameter class
    class Parameters:
        moviename = ""
        date = datetime.now

    def __init__(self):
        pass

    def __send_query(self, query):
        endpoint = "https://query.wikidata.org/sparql?format=json&query="
        url = endpoint + encodeurl.quote(query)
        res = requests.get(url).json()
        value = res['results']
        return value

    def deliver(self, response):

        try:
            moviename = response["parameters"]["fields"]["movie_name"]["stringValue"]
            date = response["parameters"]["fields"]["date-period"]["endDate"]
        except KeyError:
            print("Could not find a movie name")
            moviename = ""
            date = datetime.today()
            # return 'Could not find a movie'

        # gets the intent name + default response from the DF response.
        intent_name = response["intent"]["displayName"]
        default_response = response["fulfillmentText"]

        print("intent name: ", intent_name)

        # Creating the universal parameter object.
        # This doesnt happen for every query though.
        parameters = Courier.Parameters()
        parameters.moviename = moviename
        parameters.date = date

        # Assign function names to viariables so they won't be called during assignment
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
            print ("Got here once \n")
            if (sparql_result[0] == False):
                return [True, [default_response]]
        except:
            return [True, [default_response]]

        return sparql_result

    # Return the movie that won the Oscar in a given year
    # Will return a single string.
    def __query_oscar_movies(self, response):
        year_string = response["parameters"]["fields"]["date-period"]["structValue"]["fields"]["endDate"]["stringValue"]
        year = year_string[:4]

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
                res['bindings'][0]['movieLabel']['value']
            ]
        ]

    # Return the Oscar winners for a given year
    # Will return an array containing both male and female
    # eg ['Rami Malek', 'Olivia Colman']
    def __query_oscar_winner(self, response):
        year_string = response["parameters"]["fields"]["date-period"]["structValue"]["fields"]["endDate"]["stringValue"]
        year = year_string[:4]
        print("============YEAR ==========", year)

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

        res1 = self.__send_query(query_male_actor)
        res2 = self.__send_query(query_female_actor)

        return [
            True,
            [
                res1['bindings'][0]['actorLabel']['value'],
                res2['bindings'][0]['actorLabel']['value']
            ]
        ]

    def __query_movie_release_date(self, params):
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
        """ % (params.moviename.lower())

        res = self.__send_query(query)

        results = []
        for v in res["bindings"]:
            output = {
                "moviename": v["itemLabel"]["value"],
                "year": v["year"]["value"]
            }
            results.append(output)

        return results

    def __query_oscar_winner_director(self, params):
        year = str(params.date.year)
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
            FILTER((?date >= "{%s}-01-01T00:00:00Z"^^xsd:dateTime) && (?date <= "%s-12-31T00:00:00Z"^^xsd:dateTime))
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en,fr" . }
            }
        """ % (year, year)
        res = self.__send_query(query)
        res = res["bindings"]
        return res

    def __query_genre(self, params):
        pass


if __name__ == "__main__":
    courior = Courier()

    delivery = courior.deliver()
    print(delivery)
    # print(courior.query_oscar_winner_actor(2019))
