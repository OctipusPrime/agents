from openai import AzureOpenAI
import os

from Agent import Agent
from Locations import ControlRoom, EngineRoom
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
control_room = ControlRoom(world=world)
engine_room = EngineRoom(world=world)
world.add_location(control_room)
world.add_location(engine_room)
agent.current_location = control_room

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
                {"role": "assistant", "content": message.content},
                {"role": "user", "content": nudge_prompt},
            ])
            world.number_of_nudges += 1
    print("Nudges exhausted!")

if __name__ == "__main__":
    main()

