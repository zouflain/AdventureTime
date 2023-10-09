from entity import EntityManager
from components import *
import numpy as np

class Room:
    def __init__(self,width: int, height: int):
        self.width = width
        self.height = height


class Tile:
    def __init__(self, tid: int, ttype: str = "open"):
        self.id = tid
        self.type = ttype


class RoomGenerator:
    def __init__(self, width: int, height: int):
        self.tiles = [Tile(i) for i in range(0, width*height)]


class LevelGenerator:
    def __init__(self, width: int, height: int):
        self.tile_entities = EntityManager.genIDs(width*height)

        #after
        for i,tile in enumerate(self.tile_entities):
            x = i % width
            y = int(i / width)
            EntityManager.addComponents(
                components=[
                    TileData(),
                    RenderableDynamic(
                        meshes=["Cube"],
                        position=np.array((x*50,y*50,0),dtype=np.float32)
                    )
                ],
                eid=tile
            )
