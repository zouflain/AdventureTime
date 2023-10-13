import numpy as np
from OpenGL.GL import *
from scipy.spatial.transform import Rotation
from model import Animation


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


class DjikstraSet(BaseComponent):
    def __init__(self):
        super().__init__()
        self.walk_map = None
        self.fly_map = None
        self.sight_map = None


class HumanoidComponent(BaseComponent):
    def __init__(self, body: dict = None):
        super().__init__()
        default = {
            "head": None,
            "torso": None,
            "arm_L": None,
            "arm_R": None,
            "leg_L": None,
            "leg_R": None
        }
        self.body_parts = body if body else default.copy()
        self.defaults = default.copy()

    def getBodyMeshes(self) -> list[str]:
        return [mesh for mesh in self.body_parts.values() if mesh is not None]


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


class Renderable(BaseComponent):
    def __init__(self, position: np.array = np.zeros(3, dtype=np.float32), meshes: list[str] = []):
        super().__init__()
        self.meshes = meshes.copy()
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

    def assign(self, eid: int) -> None:
        super().assign(eid)
        self.reconstruct()  #_eid needs to be passed into the uniform buffer object

    def reconstruct(self) -> None:
        rot = Rotation.from_euler("xyz", self.euler, True).as_matrix()
        self.matrix = np.array(
            (
                (rot[0][0], rot[0][1], rot[0][2], self.position[0]),
                (rot[1][0], rot[1][1], rot[1][2], self.position[1]),
                (rot[2][0], rot[2][1], rot[2][2], self.position[2]),
                (0, 0, 0, 1),
                self._eid
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


class RenderableDynamic(Renderable):
    def __init__(self, position: np.array = np.zeros(3, dtype=np.float32), meshes: list[str] = [], armature: str = "Default"):
        super().__init__(position, meshes)
        self.animation = None
        self.next_frame = 0
        self.armature = armature

        arr = np.zeros(1, dtype=np.uint)
        glCreateBuffers(1, arr)
        self.animation_ssbo = arr[0]
        glNamedBufferStorage(self.animation_ssbo, Animation.RENDER_BONE_TYPE.itemsize*Animation.MAX_BONES, None, GL_DYNAMIC_STORAGE_BIT)

"""
class Renderable3D(BaseComponent):
    def __init__(self, position: np.array = np.zeros(3, dtype=np.float32), meshes: list[str] = [], armature: str = "Default"):
        super().__init__()
        self.animation = None
        self.next_frame = 1
        self.meshes = meshes.copy()
        self.armature = armature

        arr = np.zeros(2, dtype=np.uint)
        glCreateBuffers(2, arr)
        self.ubo = arr[0]
        self.animation_ssbo = arr[1]

        glNamedBufferStorage(self.animation_ssbo, Animation.RENDER_BONE_TYPE.itemsize*Animation.MAX_BONES, None, GL_DYNAMIC_STORAGE_BIT)

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
"""

class RoomComponent(BaseComponent):
    def __init__(self):
        super().__init__()



class TileData(BaseComponent):
    def __init__(self):
        super().__init__()
