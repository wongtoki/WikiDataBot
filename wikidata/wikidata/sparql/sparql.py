import requests
from datetime import datetime
import json
import urllib.parse as encodeurl


class Courior:

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

    def deliver(self, response, moviename="", date=datetime.today()):

        


        intent_name = response["intent"]["displayName"]
        default_response = response["fulfillmentText"]

        # Creating the universal parameter object.
        parameters = Courior.Parameters()
        parameters.moviename = moviename
        parameters.date = date

        # Assign function names to viariables so they won't be called during assignment
        ask_oscar_winner_movie = self.__query_oscar_movies
        ask_academy_award_winner_male = self.__query_academy_award_winner_male
        ask_academy_award_winner_female = self.__query_academy_award_winner_female
        ask_release_date = self.__query_movie_release_date
        ask_oscar_winner_director = self.__query_oscar_winner_director

        # Using a dictionary for easy intent response
        packages = {
            "ask_oscar_winner": ask_oscar_winner_movie,
            "ask_oscar_winner_male": ask_academy_award_winner_male,
            "ask_oscar_winner_female": ask_academy_award_winner_female,
            "ask_release_date": ask_release_date,
            "ask_oscar_winner_director": ask_oscar_winner_director
        }

        # Calling the function assigned to the dictionary key
        try:
            res = packages[intent_name](parameters)
            if res == None:
                return default_response
        except:
            return default_response

        return res

    def __query_oscar_movies(self, params):
        year = str(params.date.year)
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
        return res['bindings'][0]['movieLabel']['value']

    def __query_academy_award_winner_male(self, params):
        year = str(params.date.year)
        query = """
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
        res = self.__send_query(query)
        return res['bindings'][0]['actorLabel']['value']

    def __query_academy_award_winner_female(self, params):
        year = str(params.date.year)
        query = """
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
        res = self.__send_query(query)
        return res['bindings'][0]['actorLabel']['value']

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
        print(res)
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
    courior = Courior()


    delivery = courior.deliver()
    print(delivery)
