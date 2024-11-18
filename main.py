from openai import AzureOpenAI
import os
import json

from Agent import Agent
from Locations import TestLocation
from World import World
from prompts import test_system_prompt, test_tool_use_prompt
client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),
  api_version="2024-08-01-preview"
)
world = World()
agent = Agent(client=client, system_prompt=test_system_prompt)
test_location = TestLocation()
print(test_location.available_actions)
world.add_location(test_location)
agent.current_location = test_location

def main():
    message = agent.respond(test_tool_use_prompt)
    print(message)
    print(agent.inventory)

if __name__ == "__main__":
    main()

