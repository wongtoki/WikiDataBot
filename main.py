from agent import Agent
import requests
import json
from wikidata.wikidata.sparql.sparql import Courier

agent = Agent('SDHSJALSN','en')

def console(courier):
	userInput = input("Talk to me:")
	if userInput != "EXIT":
		response = agent.ask_json(userInput)
		parsed = json.loads(response.text)
		delivery = courier.deliver(parsed)
		print(delivery)
		console(courier)

def main():

	#Get a response from the dialogflow agent
	# res = agent.ask_response_text("Hello")
	# print(res)
	courier = Courier()
	console(courier)

	



if __name__ == "__main__":
	main()