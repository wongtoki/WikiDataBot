import requests
import json
import urllib.parse as encodeurl


class Courior:

    def __init__(self):
        pass

    def __send_query(self, query):
        endpoint = "https://query.wikidata.org/sparql?format=json&query="
        url = endpoint + encodeurl.quote(query)
        res = requests.get(url)
        return res.json()

    def query_oscar_movies(self, year):
        year = str(year)
        query = """
            SELECT ?movie ?movieLabel
            WHERE
            {
            ?movie p:P166 ?awardstatement .
            ?movie wdt:P31 wd:Q11424 .
            ?awardstatement ps:P166 wd:Q102427  .
            FILTER((?date >= "%s-01-01T00:00:00Z"^^xsd:dateTime) && (?date <= "%s-12-31T00:00:00Z"^^xsd:dateTime))
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en,fr" . }
            }
        """ % (year, year)
        print(query)
        res = self.__send_query(query)

        # data = {
        #     "name":res["results"]["movieLabel"]["value"]
        # }

        print(res)




if __name__ == "__main__":
    courior = Courior()
    print(courior.query_oscar_movies(2019))
    pass
