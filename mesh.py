from OpenGL.GL import *
import numpy as np
import json as JSON


class Mesh:
    def __init__(self, verts: np.array, stride: int, faces: np.array, shader: int, texture: int):

        # Generate OpenGL Data
        self.shader = shader
        self.vbo = glGenBuffers(1)
        self.vbo_i = glGenBuffers(1)
        self.vao = glGenVertexArrays(1)
        self.faces = faces
        self.verts = verts
        self.nfaces = faces.size
        self.nverts = verts.size
        self.texture = texture
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_i)

        # Load vertex data
        glBufferData(GL_ARRAY_BUFFER, self.verts.nbytes, self.verts, GL_STATIC_DRAW)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.faces.nbytes, self.faces, GL_STATIC_DRAW)

        # Model space coordinates
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))

        # Model space normals
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))

        # Bone Indexes
        glEnableVertexAttribArray(2)
        glVertexAttribIPointer(2, 4, GL_UNSIGNED_INT, stride, ctypes.c_void_p(24))

        # Bone Weights
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 4, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(40))

        # Texture Coordinates
        glEnableVertexAttribArray(4)
        glVertexAttribPointer(4, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(56))

        # Texture Coordinates
        glEnableVertexAttribArray(5)
        glVertexAttribPointer(5, 4, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(64))

        #Cleanup
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        glUseProgram(0)

    @staticmethod
    def fromFile(game, fname: str) -> bool:
        success = False
        try:
            with open(fname) as file:
                json = JSON.load(file)
                for json_mesh in json["meshes"]:
                    name = json_mesh["info"]["name"]
                    json_verts = json_mesh["verts"]
                    json_faces = json_mesh["faces"]
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
                        faces=np.array(
                            json_faces,
                            dtype=np.uint
                        ),
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
                        ),
                        stride=dtype.itemsize
                    )
                    game.meshes[name] = mesh
                    success = True
        except:
            pass
        return success

    def preRender(self):
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_i)
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def render(self, ubo):
        glBindBufferBase(GL_UNIFORM_BUFFER, 0, ubo)
        glDrawElements(GL_TRIANGLES, self.nfaces, GL_UNSIGNED_INT, ctypes.c_void_p(0))


    @staticmethod
    def postRender():
        glBindTexture(GL_TEXTURE_2D, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    '''
    def render(self, model, view, projection,lights):

        # Init
        glUseProgram(self.shader)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_i)
        glBindTexture(GL_TEXTURE_2D, self.texture)


        # Uniforms
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "model"), 1, GL_FALSE, model)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "view"), 1, GL_FALSE, view)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "projection"), 1, GL_FALSE, projection)

        # Lights
        glUniform3fv(
            glGetUniformLocation(self.shader, "diffuse"),
            4 if len(lights) > 4 else len(lights),
            np.array(
                [light.diffuse for light in lights],
                dtype=np.dtype([("diffuse", (np.float32, 3))])
            )
        )
        glUniform3fv(
            glGetUniformLocation(self.shader, "ambient"),
            4 if len(lights) > 4 else len(lights),
            np.array(
                [light.ambient for light in lights],
                dtype=np.dtype([("ambient", (np.float32, 3))])
            )
        )
        glUniform3fv(
            glGetUniformLocation(self.shader, "position"),
            4 if len(lights) > 4 else len(lights),
            np.array(
                [light.position for light in lights],
                dtype=np.dtype([("position", (np.float32, 3))])
            )
        )


        # Render
        glDrawElements(GL_TRIANGLES, self.nfaces, GL_UNSIGNED_INT, ctypes.c_void_p(0))

        # Clean up
        glBindTexture(GL_TEXTURE_2D, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        glUseProgram(0)
    '''
