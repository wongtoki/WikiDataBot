from agent import Agent
import requests
import json

agent = Agent('test','en')

def console():
	userInput = input("Talk to me:")
	if userInput != "EXIT":
		response = agent.ask_json(userInput)
		print(response.text)
		console()

def main():

	#Get a response from the dialogflow agent
	# res = agent.ask_response_text("Hello")
	# print(res)

	console()

	



if __name__ == "__main__":
	main()