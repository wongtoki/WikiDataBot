import requests
from datetime import datetime
import json
import urllib.parse as encodeurl


class Courior:

    #This class is used as a universal parameter class
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

    def deliver(self, intent, moviename = "", date = datetime.today()):
        
        #Creating the universal parameter object. 
        parameters = Courior.Parameters()
        parameters.moviename = moviename
        parameters.date = date

        #Assign function names to viariables so they won't be called during assignment
        ask_oscar_winner_movie = self.query_oscar_movies
        ask_academy_award_winner = self.query_academy_award_winner

        #Using a dictionary for easy intent response 
        packages = {
            "ask_oscar_winner":ask_oscar_winner_movie,
            "ask_academy_winner":ask_academy_award_winner
        }
        
        #Calling the function assigned to the dictionary key
        return packages[intent](parameters)

    def query_oscar_movies(self, params):
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
        return res['bindings']

    def query_academy_award_winner(self, params):
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

if __name__ == "__main__":
    courior = Courior()
    delivery = courior.deliver("ask_academy_winner", date=datetime(2019,1,1))
    print(delivery)
