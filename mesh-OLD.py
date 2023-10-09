from __future__ import annotations
from OpenGL.GL import *
import numpy as np
import json as JSON


class Mesh:
    def __init__(self, verts: np.array, shader: int, texture: int):

        # Generate OpenGL Data
        self.shader = shader
        self.verts = verts
        self.nverts = verts.size
        self.texture = texture
        arr = np.zeros(1, dtype=np.uint)
        glCreateBuffers(1, arr)
        self.ssbo = arr[0]
        glNamedBufferStorage(self.ssbo, verts.nbytes, verts, 0)
        print(f"Verts: {self.nverts} {'' if self.nverts>36 else self.verts}")

        #Cleanup
        glUseProgram(0)

    @staticmethod
    def fromDict(game, data: dict) -> Mesh:
        return Mesh(
            texture=game.getTexture(data["info"]["texture"]),
            shader=game.shaders.get(data["info"]["shader"], 0),
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
                        shader=game.shaders.get(json_mesh["info"]["shader"], 0),
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

    def preRender(self):
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 3, self.ssbo)

    def render(self):
        glDrawArrays(GL_TRIANGLES, 0, self.nverts)

