from openai import AzureOpenAI
import os
import json

from Agent import Agent
from Locations import EntryWay
from World import World
from prompts import system_prompt, goal_prompt, nudge_prompt
client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),
  api_version="2024-08-01-preview"
)

# Instantiate world, agent, and locations
agent = Agent(client=client)
world = World(agent=agent)
entryway = EntryWay(world=world)
print(entryway.available_actions)
world.add_location(entryway)
agent.current_location = entryway

def main():
    # Set up initial state
    agent.messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": goal_prompt},
        {"role": "user", "content": agent.current_location.description}
    ]
    # Run agent loop until task is complete or nudges are exhausted
    while world.number_of_nudges < 3:
        # If task is complete, break
        if world.check_for_completion():
            print("Goal complete!")
            break
        # Let agent make a choice
        message = agent.act()
        # Check if agent made a tool call
        if not message.tool_calls:
            print("Pre-nudge message:", message.content)
            # Nudge agent
            agent.messages.extend([
                {"role": "user", "content": nudge_prompt},
            ])
            world.number_of_nudges += 1

if __name__ == "__main__":
    main()

