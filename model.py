from __future__ import annotations
from OpenGL.GL import *
import numpy as np
import json as JSON

class Mesh:
    def __init__(self, verts: np.array, texture: int):

        # Generate OpenGL Data
        self.verts = verts
        self.nverts = verts.size
        self.texture = texture
        arr = np.zeros(1, dtype=np.uint)
        glCreateBuffers(1, arr)
        self.ssbo = arr[0]
        glNamedBufferStorage(self.ssbo, verts.nbytes, verts, 0)

        #Cleanup
        glUseProgram(0)

    @staticmethod
    def fromDict(game, data: dict) -> Mesh:
        return Mesh(
            texture=game.getTexture(data["info"]["texture"]),
            verts=np.array(
                [
                    (
                        vert["pos"],
                        vert["nrm"],
                        vert["ind"],
                        vert["wgt"],
                        vert["uvs"],
                        vert["clr"]
                    ) for vert in data["verts"]
                ],
                dtype=np.dtype(
                    [
                        ("pos", (np.float32, 3)),
                        ("normal", (np.float32, 3)),
                        ("indexes", (np.uint, 4)),
                        ("weights", (np.float32, 4)),
                        ("uv_coords", (np.float32, 2)),
                        ("color", (np.float32, 4))
                    ]
                )
            )
        )


    '''
    @staticmethod
    def fromFile(game, fname: str) -> bool:
        success = False
        try:
            with open(fname) as file:
                json = JSON.load(file)
                for json_mesh in json["meshes"]:
                    name = json_mesh["info"]["name"]
                    json_verts = json_mesh["verts"]
                    dtype = np.dtype(
                        [
                            ("pos", (np.float32, 3)),
                            ("normal", (np.float32, 3)),
                            ("indexes", (np.uint, 4)),
                            ("weights", (np.float32, 4)),
                            ("uv_coords", (np.float32, 2)),
                            ("color", (np.float32, 4))
                        ]
                    )
                    mesh = Mesh(
                        texture=game.getTexture(json_mesh["info"]["texture"]),
                        verts=np.array(
                            [
                                (
                                    json_vert["pos"],
                                    json_vert["nrm"],
                                    json_vert["ind"],
                                    json_vert["wgt"],
                                    json_vert["uvs"],
                                    json_vert["clr"]
                                ) for json_vert in json_verts
                            ],
                            dtype=dtype
                        )
                    )
                    game.meshes[name] = mesh
                    success = True
        except:
            pass
        return success
        '''

    def preRender(self):
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 3, self.ssbo)

    def render(self):
        glDrawArrays(GL_TRIANGLES, 0, self.nverts)


class Armature:
    def __init__(self, animations: dict, bind_list: list):
        self.animations = animations
        self.bind_bones = np.array(
            [
                (
                    bone["quat"],
                    bone["pos"]
                ) for bone in bind_list
            ],
            dtype=Animation.BONE_TYPE
        )
        buffers = np.zeros(1, dtype=np.uint)
        glCreateBuffers(1, buffers)
        self.bind_ssbo = buffers[0]
        glNamedBufferData(self.bind_ssbo, self.bind_bones.nbytes, self.bind_bones, GL_STATIC_DRAW)


class Animation:
    MAX_BONES = 200
    BONE_TYPE = np.dtype(
        [
            ("quat", (np.float32, 4)),
            ("pos", (np.float32, 3))
        ]
    )
    RENDER_BONE_TYPE = np.dtype(
        [
            ("rotation", (np.float32, 9)),
            ("translation", (np.float32, 3)),
            ("bind_pos", (np.float32, 3))
        ]
    )

    def __init__(self, bind_bones: np.array, frames: list[dict]):
        self.bind_bones = bind_bones
        self.frames = frames
        size = len(frames)
        buffers = np.zeros(size, dtype=np.uint)
        glCreateBuffers(size, buffers)
        for i, frame in enumerate(frames):
            frame["ssbo"] = buffers[i]
            bones = frame["bones"]
            glNamedBufferData(buffers[i], len(bones)*self.BONE_TYPE.itemsize, bones, GL_STATIC_DRAW)

    def compute(self, ssbo: int) -> None:
        pass

    @classmethod
    def fromDict(cls, game, data: dict) -> Animation:
        frames = []
        for f_data in data["keyframes"]:
            frames.append(
                {
                    "frame": f_data["start"],
                    "bones": np.array(
                        [(bone["quat"], bone["pos"]) for bone in f_data["bones"]],
                        dtype=cls.BONE_TYPE
                    )
                }
            )
        return Animation(
            frames=frames,
            bind_bones=np.array(
                [(bone["quat"], bone["pos"]) for bone in f_data["bones"]],
                dtype=cls.BONE_TYPE
            )
        )