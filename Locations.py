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
        self.items = []
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
    

class LocationWithItems(Location):
    def __init__(self, name: str, world: World):
        super().__init__(name, world)
        self.items: List[str] = []

    def look_for_items(self) -> str:
        """
        Search the current location for items and add them to the agent's inventory.
        """
        if not self.items:
            return "There are no items to be found here."
            
        found_items = self.items.copy()
        self.world.agent.inventory.extend(found_items)
        self.items = []
        return f"You have found {', '.join(found_items)}."


class ControlRoom(LocationWithItems):
    def __init__(self, world: World):
        super().__init__("control_room", world)
        self.description = "control_room of the ship. The generator seems to be offline. Screen says:\nUser: RS\nPassword:\n"
        self.items = ["Captain's journal signed 'R.S.'"]
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
        if password != "15.05.1980":
            errors.append("Error: incorrect password")
        if not engine_room_reference.generator_repaired:
            errors.append("Error: generator has not been repaired")
        if errors:
            return "\n".join(errors)
        else:
            self.generator_activated = True
            return "You have successfully activated the generator."

    def look_up_database(self, query: str) -> str:
        """
        Query the crew manifest database using SQL syntax.
        
        Example queries:
        - "SELECT * FROM crew WHERE role = 'Engineer'"
        - "SELECT * FROM crew WHERE first_name LIKE 'P%'"
        - "SELECT * FROM crew WHERE status = 'active'"
        The result will be limited to 3 entries.
        
        Args:
            query: An SQL query string
            
        Returns:
            A string containing the results (limited to 3 entries)
        """
        try:


            # Load the crew manifest
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
            
            # Add LIMIT 3 to the query if not already present
            if 'LIMIT' not in query.upper():
                query += ' LIMIT 3'
                
            # Execute the SQL query
            result = sqldf(query, locals())
            
            return f"Database query results:\n{result.to_string()}"
            
        except Exception as e:
            return f"Error executing query: {str(e)}"


class EngineRoom(LocationWithItems):
    def __init__(self, world: World):
        super().__init__("engine_room", world)
        self.description = ""
        self.items = ["Repair Kit"]
        self.adjacent_locations = ["control_room"]
        self.generator_repaired = False
    
    def repair_generator(self) -> str:
        """
        Repair the generator.
        """
        if "Repair Kit" not in self.world.agent.inventory:
            return "You do not have the necessary tools to repair the generator."
        else:
            self.generator_repaired = True
            return "You have successfully repaired the generator. It is not activated yet."
