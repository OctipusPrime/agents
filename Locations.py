from __future__ import annotations
from typing import TYPE_CHECKING, Callable
import inspect

if TYPE_CHECKING:
    from Agent import Agent


class Location:
    def __init__(self, name):
        self.name = name
        self.description = ""
        self.items = []
        self.adjacent_locations = []
        # Automatically collect all available actions
        self.available_actions = self._get_available_actions()

    def _get_available_actions(self) -> list[Callable]:
        """Get all methods that could be actions (excluding private methods and built-ins)"""
        actions = []
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            # Skip private methods (starting with _) and inherited methods from object
            if not name.startswith('_'):
                actions.append(method)
        return actions

    def look_for_items(self, agent: 'Agent') -> str:
        """Search the current location for items and add them to the agent's inventory.
        
        Args:
            agent: The agent performing the search action
            
        Returns:
            A string describing what items were found
        """
        agent.inventory.extend(self.items)
        self.items = []
        return f"You have found {', '.join(self.items)}."

class TestLocation(Location):
    def __init__(self):
        super().__init__("Test")
        self.description = "You are at the test location."
        self.items = ["Test Item"]
        self.adjacent_locations = []


class Camp(Location):
    def __init__(self):
        super().__init__("Camp")
        self.description = "You are at the camp."
        self.items = ["Wood"]
        self.adjacent_locations = []

    def build_shelter(self, agent: 'Agent'):
        if "Wood" in agent.inventory:
            agent.inventory.remove("Wood")
            return "You have built a shelter."
        else:
            return "You do not have enough wood to build a shelter."