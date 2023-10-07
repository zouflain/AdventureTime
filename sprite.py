from OpenGL.GL import *
import numpy as np

class Sprite:

    shader = 0
    vbo = 0
    vao = 0

    def __init__(self):

        # Generate OpenGL Data
        if not self.shader:
            self.shader = 0
            self.vbo = glGenBuffers(1)
            self.vao = glGenVertexArrays(1)
            glBindVertexArray(self.vao)
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

            # Load vertex data
            self.verts = np.array(
                (
                    0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0
                ),
                dtype=np.float
            )
            glBufferData(GL_ARRAY_BUFFER, self.verts.nbytes, self.verts, GL_STATIC_DRAW)
            stride = 4*4

            # Model space coordinates
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))

            # Texture Coordiantes
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(8))

            #Cleanup
            glBindVertexArray(0)
            glUseProgram(0)

    def render(self, modelview, projection):

        # Init
        glUseProgram(self.shader)
        glBindVertexArray(self.vao)

        # Uniforms
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "modelview"), 1, GL_FALSE, modelview)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "projection"), 1, GL_FALSE, projection)

        # Render
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

        # Clean up
        glBindVertexArray(0)
        glUseProgram(0)
        