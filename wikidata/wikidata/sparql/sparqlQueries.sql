
-- Movie that won the Oscar in  2019 - given year
SELECT ?movie ?movieLabel ?date 
WHERE
{
  ?movie p:P166 ?awardstatement .
  ?movie wdt:P31 wd:Q11424 .
  ?awardstatement ps:P166 wd:Q102427  .
  ?awardstatement pq:P585 ?date .
#   ?awardstatement pq:P1686 ?forWork .
  FILTER((?date >= "2019-01-01T00:00:00Z"^^xsd:dateTime) && (?date <= "2019-12-31T00:00:00Z"^^xsd:dateTime))
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,fr" . }
}
LIMIT 10


-- Academy award for best actor
SELECT ?actor ?actorLabel ?date ?forWork ?forWorkLabel
WHERE
{
  # find a human
  ?actor wdt:P31 wd:Q5 
  ?actor p:P166 ?awardstatement .
  ?awardstatement ps:P166 wd:Q103916 .
  ?awardstatement pq:P585 ?date .
  ?awardstatement pq:P1686 ?forWork .
  FILTER((?date >= "2019-01-01T00:00:00Z"^^xsd:dateTime) && (?date <= "2019-12-31T00:00:00Z"^^xsd:dateTime))
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,fr" . 
}}


-- Award for best actress in 2019
SELECT ?actor ?actorLabel ?date ?forWork ?forWorkLabel
WHERE
{
  # find a human
  ?actor wdt:P31 wd:Q5 .
  ?actor p:P166 ?awardstatement .
  ?awardstatement ps:P166 wd:Q103618 .
  ?awardstatement pq:P585 ?date .
  ?awardstatement pq:P1686 ?forWork .
  FILTER((?date >= "2019-01-01T00:00:00Z"^^xsd:dateTime) && (?date <= "2019-12-31T00:00:00Z"^^xsd:dateTime))
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,fr" . }
}



-- Award for the best director in 2018
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
  FILTER((?date >= "2018-01-01T00:00:00Z"^^xsd:dateTime) && (?date <= "2019-12-31T00:00:00Z"^^xsd:dateTime))
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,fr" . }
}