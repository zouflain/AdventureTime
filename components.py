import numpy as np
from OpenGL.GL import *
from scipy.spatial.transform import Rotation


class BaseComponent:
    def __init__(self):
        self._eid = 0

    def assign(self, eid: int) -> None:
        self.entries[eid] = self
        self._eid = eid

    def getID(self) -> int:
        return self._eid

    def __init_subclass__(cls, **kwargs):
        if not hasattr(cls, "entries"):
            cls.entries = {}

    @classmethod
    def remove(cls, eid: int):
        del cls.entries[eid]

    @classmethod
    def get(cls, eid: int):
        out = None
        if eid in cls.entries:
            out = cls.entries[eid]
        return out

# Try to keep alphabetized

class CurrentRoom(BaseComponent):
    def __init__(self, entities: list[int] = []):
        super().__init__()
        self.entities = entities


class Level(BaseComponent):
    def __init__(self, tiles: set):
        super().__init__()
        self.tiles = tiles
        self.contents = tiles.copy() # Starts OFF as a copy, but will change


class LightSource(BaseComponent):
    def __init__(self, position: np.array = np.empty(3), ambient: np.array = np.empty(3),
                 diffuse: np.array = np.empty(3)):
        super().__init__()
        self.position = position
        self.ambient = ambient
        self.diffuse = diffuse


class DjikstraSet(BaseComponent):
    def __init__(self):
        super().__init__()
        self.walk_map = None
        self.fly_map = None
        self.sight_map = None

class Renderable(BaseComponent):
    def __init__(self):
        super().__init__()
        self.animation = "none"
        self.keyframe = 0
        self.material = "none"


class Renderable3D(BaseComponent):
    def __init__(self, meshes: list[str] = [], position: np.array = np.zeros(3, dtype=np.float32)):
        super().__init__()
        self.meshes = meshes

        # CANT JUST GENERATE ONE!?
        arr = np.zeros(1, dtype=np.uint)
        glCreateBuffers(1, arr)
        self.ubo = arr[0]

        # When changing these...
        self.euler = np.array((0, 0, 0), dtype=np.float32)
        self.position = position
        self.scale = np.array((0, 0, 0), dtype=np.float32)

        # ...update this
        self.matrix = np.identity(4)
        glNamedBufferStorage(self.ubo, self.matrix.nbytes, self.matrix, GL_DYNAMIC_STORAGE_BIT | GL_MAP_READ_BIT)

        #...by calling this
        self.reconstruct()

    def assign(self,eid: int) -> None:
        super().assign(eid)
        self.reconstruct()  #_eid needs to be passed into the uniform buffer object

    def reconstruct(self) -> None:
        rot = Rotation.from_euler("xyz", self.euler, True).as_matrix()
        '''
        self.matrix = np.array(
            (
                (rot[0][0], rot[0][1], rot[0][2], self.position[0]),
                (rot[1][0], rot[1][1], rot[1][2], self.position[1]),
                (rot[2][0], rot[2][1], rot[2][2], self.position[2]),
                (0, 0, 0, 1),
            ),
            dtype=np.float32
        )
        '''
        self.matrix = np.array(
            (
                (rot[0][0], rot[0][1], rot[0][2], self.position[0]),
                (rot[1][0], rot[1][1], rot[1][2], self.position[1]),
                (rot[2][0], rot[2][1], rot[2][2], self.position[2]),
                (0, 0, 0, 1),
                (self._eid)
            ),
            dtype=np.dtype(
                        [
                            ("mat1", (np.float32, 4)),
                            ("mat2", (np.float32, 4)),
                            ("mat3", (np.float32, 4)),
                            ("mat4", (np.float32, 4)),
                            ("eid", np.int32)
                        ]
                    )
        )
        glNamedBufferSubData(self.ubo, 0, self.matrix.nbytes, self.matrix)


class RoomComponent(BaseComponent):
    def __init__(self):
        super().__init__()



class TileData(BaseComponent):
    def __init__(self):
        super().__init__()


class WorldPosition(BaseComponent):
    def __init__(self, current: np.array = None, previous: np.array = None):
        super().__init__()
        self.current = current
        self.previous = previous
