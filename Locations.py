from __future__ import annotations
from typing import TYPE_CHECKING, Callable
import inspect

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

    def look_for_items(self) -> str:
        """
        Search the current location for items and add them to the agent's inventory.
            
        Returns:
            A string describing what items were found
        """
        if not self.items:
            return "There are no items to find here."
            
        found_items = self.items.copy()
        self.world.agent.inventory.extend(found_items)
        self.items = []
        return f"You have found {', '.join(found_items)}."
    
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
        
        return f"You have moved to {location_name}. {new_location.description}"

class ControlRoom(Location):
    def __init__(self, world: World):
        super().__init__("control_room", world)
        self.description = "The control_room is the command centre of the ship. The main generator seems to be offline."
        self.items = []
        self.adjacent_locations = ["engine_room"]
        self.generator_activated = False

    def activate_generator(self) -> str:
        """
        Activate the generator.
        """
        engine_room_reference = self.world.locations.get("engine_room")
        if not engine_room_reference:
            return "Error: engine_room does not exist in the world"

        if not engine_room_reference.generator_repaired:
            return "The generator cannot be activated until it has been repaired in the engine_room."
        else:
            self.generator_activated = True
            return "You have successfully activated the generator."


class EngineRoom(Location):
    def __init__(self, world: World):
        super().__init__("engine_room", world)
        self.description = "The engine_room is dark and damp. There are pipes and valves everywhere."
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
