from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Agent import Agent


class Location:
    def __init__(self, name):
        self.name = name
        self.description = ""
        self.items = []
        self.available_actions = []
        self.adjacent_locations = []

    def look_for_items(self, agent: 'Agent'):
        agent.inventory.extend(self.items)
        self.items = []
        return f"You have found {', '.join(self.items)}."


class Camp(Location):
    def __init__(self):
        super().__init__("Camp")
        self.description = "You are at the camp."
        self.items = ["Wood"]
        self.available_actions = [self.build_shelter]
        self.adjacent_locations = []

    def build_shelter(self, agent: 'Agent'):
        if "Wood" in agent.inventory:
            agent.inventory.remove("Wood")
            return "You have built a shelter."
        else:
            return "You do not have enough wood to build a shelter."