from openai import AzureOpenAI
from Locations import Location
from utils import function_to_schema

import json
import inspect

class Agent:
    def __init__(self, client: AzureOpenAI):
        self.inventory = []
        self.current_location: Location = None
        self.client: AzureOpenAI = client
        self.messages = None

    def _resolve_tool_call(self, tool_call, tools_map):
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        print(f"Agent: {name}({args})")

        # Check if the function exists in the tools map
        if name not in tools_map:
            return f"Error: The action '{name}' is not available at this location."

        # Get the bound method from the location
        method = tools_map[name]
        
        # If the method requires the agent parameter, include it
        if 'agent' in inspect.signature(method).parameters:
            args['agent'] = self
        
        # Call the bound method with the arguments
        return method(**args)

    def act(self):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=self.messages,
            temperature=0.4,
            tools=[function_to_schema(action) for action in self.current_location.available_actions]
        )
        self.messages.append(response.choices[0].message)
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                # Create a map of function names to bound methods
                tool_map = {
                    action.__name__: action.__get__(self.current_location, type(self.current_location))
                    for action in self.current_location.available_actions
                }
                result = self._resolve_tool_call(tool_call, tool_map)
                self.messages.append(
                    {"role": "tool", 
                     "tool_call_id": tool_call.id,
                     "content": result})
                if tool_call.function.name != "think":
                    print(result)
        return response.choices[0].message
