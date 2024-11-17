from Locations import Location


class World:
    def __init__(self):
        self.locations = {}

    def add_location(self, location: Location):
        self.locations[location.name] = location
