from Locations import Location
from Agent import Agent

class World:
    def __init__(self, agent: Agent):
        self.locations = {}
        self.number_of_nudges = 0
        self.agent = agent
    
    def add_location(self, location: Location):
        self.locations[location.name] = location

    def check_for_completion(self) -> bool:
        entryway = self.locations.get('Entryway')
        if entryway and entryway.door_unlocked:
            return True
        return False
