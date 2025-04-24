from node import *

class Segment:
    def __init__ (self, name, origin, destination):
        self.name = name
        self.origin = origin
        self.destination = destination
        self.cost = round(Distance(origin, destination), 2)