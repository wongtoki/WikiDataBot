from agent import Agent
import json

agent = Agent()

def main():

	#Get a response from the dialogflow agent
	res = agent.ask_intent("Hello")
	print(res)


if __name__ == "__main__":
	main()