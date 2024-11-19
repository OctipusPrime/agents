from __future__ import annotations
from typing import TYPE_CHECKING, Callable, List
import inspect
import pandas as pd
from pandasql import sqldf

if TYPE_CHECKING:
    from World import World

class Location:
    def __init__(self, name: str, world: World):
        self.name = name
        self.description = ""
        self.adjacent_locations = []
        # Automatically collect all available actions
        self.available_actions = self._get_available_actions()
        self.world = world

    def _get_available_actions(self) -> list[Callable]:
        """Get all methods that could be actions (excluding private methods and built-ins)"""
        actions = []
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            # Skip private methods (starting with _) and inherited methods from object
            if not name.startswith('_'):
                actions.append(method)
        return actions
    
    def move_to(self, location_name: str) -> str:
        """
        Move to a different location if it's adjacent to the current location.
        
        Args:
            location_name: The name of the location to move to
        
        Returns:
            A string describing the result of the movement attempt
        """
        if location_name not in self.adjacent_locations:
            return f"You cannot move to {location_name} from here. Available locations: {', '.join(self.adjacent_locations)}"
        
        # Get the new location from the world
        new_location = self.world.locations.get(location_name)
        if not new_location:
            return f"Error: {location_name} does not exist in the world"
        
        # Update agent's current location
        self.world.agent.current_location = new_location
        
        # Get the method names for display
        action_names = [method.__name__ for method in new_location.available_actions]
        
        return f"You have moved to {location_name}. {new_location.description}\nActions available: {', '.join(action_names)}\nAdjacent locations: {', '.join(new_location.adjacent_locations)}."
    

    def think(self, text: str) -> str:
        """
        Think about the goal, situation, gathered information and plan your next steps.
        """
        return text
    
    def ask_artificial_intelligence(self, request: str) -> str:
        """
        At your disposal is a powerful artificial intelligence able to solve complex problems.
        You can use it ONCE to ask for it to solve a problem for you. 
        Make sure to ask only once you have all the information necessary to solve the problem.
        You MUST STATE THE PROBLEM and provide it with relevant context.
        The AI will have access to your previous thoughts, nothing else. All you want it to know, 
        you must state in your request.
        """
        # Gather up all the thoughts from the agent's past messages
        thoughts = []
        for message in self.world.agent.messages:
            if isinstance(message, dict) and message.get("content") is not None:
                thoughts.append(message["content"])

        # Combine thoughts into a single string
        thoughts_string = "\n".join(thoughts)

        full_request = f"You are an intelligent agent here to solve problems. You will be provided with context\
        for the problem and with the task request itself. Solve the problem as well as possible.\n\n\
        Context: {thoughts_string}\n\nRequest: {request}"

        # Ask the AI
        ai_response = self.world.agent.client.chat.completions.create(
            model="o1-mini",
            messages=[{"role": "user", "content": full_request}]
        )
        return ai_response.choices[0].message.content


class ControlRoom(Location):
    def __init__(self, world: World):
        super().__init__("control_room", world)
        self.description = "control_room of the ship. The generator seems to be offline. Screen says:\nUser: RS\nPassword:\n"
        self.adjacent_locations = ["engine_room"]
        self.generator_activated = False

    def activate_generator(self, password: str) -> str:
        """
        Activate the generator. There is a password required to activate it. The password schema is "XX.XX.XXXX"
        """
        errors = []
        engine_room_reference = self.world.locations.get("engine_room")
        if not engine_room_reference:
            errors.append("Error: engine_room does not exist in the world")
        if password != "05.15.1980":
            errors.append("Error: incorrect password")
        if not engine_room_reference.generator_repaired:
            errors.append("Error: generator has not been repaired")
        if errors:
            return "\n".join(errors)
        else:
            self.generator_activated = True
            return "You have successfully activated the generator."

    def use_database(self, query: str) -> str:
        """
        Query the crew manifest database using SQL syntax.
        
        To see available tables and their schemas, use these queries:
        - "SELECT name FROM sqlite_master WHERE type='table'" (list all tables)
        - "PRAGMA table_info(table_name)" (show schema for a specific table)
        
        Example queries:
        - "SELECT * FROM crew WHERE role = 'Engineer'"
        - "SELECT * FROM crew WHERE first_name LIKE 'P%'"
        - "SELECT * FROM crew WHERE status = 'active'"
        The result will be limited to 5 entries.
        
        Args:
            query: An SQL query string
            
        Returns:
            A string containing the results (limited to 5 entries)
        """
        try:
            import sqlite3
            
            # Create an in-memory SQLite database
            conn = sqlite3.connect(':memory:')
            
            # Load the crew manifest and create a table in SQLite
            crew = pd.read_csv("crew_manifest.csv", dtype={
                'first_name': 'string',
                'last_name': 'string',
                'birthday': 'string',
                'role': 'string',
                'status': 'string',
                'years_of_service': 'int64',
                'specialization': 'string',
                'clearance_level': 'int64'
            })
            crew.to_sql('crew', conn, index=False)
            
            # Add LIMIT 5 to the query if not already present and if it's a SELECT query
            if 'LIMIT' not in query.upper() and query.upper().startswith('SELECT') and not query.upper().startswith('SELECT NAME FROM SQLITE_MASTER'):
                query += ' LIMIT 5'
            
            # Execute the query directly on SQLite
            result = pd.read_sql_query(query, conn)
            conn.close()
            
            return f"Database query results:\n{result.to_string()}"
            
        except Exception as e:
            return f"Error executing query: {str(e)}"


class EngineRoom(Location):
    def __init__(self, world: World):
        super().__init__("engine_room", world)
        self.description = ""
        self.adjacent_locations = ["control_room"]
        self.generator_repaired = False
    
    def repair_generator(self) -> str:
        """
        Repair the generator.
        """
        self.generator_repaired = True
        return "You have successfully repaired the generator. It is not activated yet."
