from openai import AzureOpenAI
import os

from Agent import Agent
from Locations import Location
from World import World
from prompts import test_system_prompt
client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),
  api_version="2024-08-01-preview"
)
world = World()
agent = Agent(client=client, system_prompt=test_system_prompt)

def main():
    message = agent.respond("Hello, I'm a new agent!")
    print(message.content)

if __name__ == "__main__":
    main()

