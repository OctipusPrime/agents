from openai import AzureOpenAI
from Locations import Location
from utils import function_to_schema

class Agent:
    def __init__(self, client: AzureOpenAI, system_prompt: str):
        self.inventory = []
        self.current_location: Location = None
        self.client: AzureOpenAI = client
        self.system_prompt = system_prompt
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def respond(self, message: str):
        self.messages.append({"role": "user", "content": message})
        response = self.client.chat.completions.create(
            model="gpt-4o-2",
            messages=self.messages,
            #tools=[function_to_schema(action) for action in self.current_location.available_actions]
        )
        return response.choices[0].message