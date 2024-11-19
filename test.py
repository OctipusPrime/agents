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
print(engine_room.available_actions)
world.add_location(control_room)
world.add_location(engine_room)
agent.current_location = control_room


print(control_room.use_database("SELECT * FROM crew WHERE role = 'Captain'"))