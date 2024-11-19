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
        control_room = self.locations.get('control_room')
        if control_room and control_room.generator_activated:
            return True
        return False
