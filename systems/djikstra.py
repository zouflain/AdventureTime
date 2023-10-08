from systems.basesystem import BaseSystem
from systems.listener import Listener
from gameevents import *
from components import *
from entity import EntityManager

class DijkstraSystem(BaseSystem):
    def __init__(self, game):
        self.listener = Listener(100, self.rebuildDjikstras)
        game.addListener(RebuildDjikstraEvent, self.listener)


    def rebuildDjikstras(self, game) -> bool:
        current_room = RoomComponent.get(game.current_room)
        if current_room:
            djikstras = [DjikstraSet.get(entity) for entity in EntityManager.findEntities([DjikstraSet])]

        return False
