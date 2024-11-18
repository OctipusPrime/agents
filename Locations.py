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
        """Search the current location for items and add them to the agent's inventory.
            
        Returns:
            A string describing what items were found
        """
        found_items = self.items.copy()
        self.world.agent.inventory.extend(found_items)
        self.items = []
        return f"You have found {', '.join(found_items)}."

class TestLocation(Location):
    def __init__(self, world: World):
        super().__init__("Test", world)
        self.description = "You are at the test location."
        self.items = ["Test Item"]
        self.adjacent_locations = []

class EntryWay(Location):
    def __init__(self, world: World):
        super().__init__("Entryway", world)
        self.description = "You are at the entryway. There is a locked door and a table with some objects on it."
        self.items = ["Key"]
        self.adjacent_locations = []
        self.door_unlocked = False  

    def unlock_door(self) -> str:
        """
        Unlock the door under the condition that the agent has the key.

        Returns:
            A string describing the result of the action
        """
        if "Key" in self.world.agent.inventory:
            self.door_unlocked = True 
            return "You have unlocked the door."
        else:
            return "You do not have the key to unlock the door."

