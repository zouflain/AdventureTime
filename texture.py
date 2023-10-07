from __future__ import annotations
from PyQt6.QtGui import QImage
from PyQt6 import QtOpenGL
from OpenGL.GL import *
import numpy as np


class Texture:
    def __init__(self, gl_tex: int, image: QImage):
        self.gl_tex = 0
        self.image = image

    @staticmethod
    def fromFile(file: str) -> Texture:
        image = QtOpenGL.QOpenGLTexture(QImage(file).mirrored())
        return Texture(image.textureId(), image)


class FBO(Texture):
    def __init__(self, width: int, height: int, internal: int, gl_type: int):
        self.fbo = 0
        self.gl_tex = 0

        # Generate FBO info
        arr = np.zeros(1, dtype=np.uint)
        glGenFramebuffers(1, arr)
        self.fbo = arr[0]

        glGenTextures(1, arr)
        self.gl_tex = arr[0]

        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glBindTexture(GL_TEXTURE_2D, self.gl_tex)

        glTexImage2D(GL_TEXTURE_2D, 0, internal, width, height, 0, GL_RGB, gl_type, None);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.gl_tex, 0)

        #cleanup
        glBindTexture(GL_TEXTURE_2D, 0)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        super().__init__(self.gl_tex)

    def __del__(self):
        glDeleteFramebuffers(1, np.array(self.fbo, dtype=np.uint))
        glDeleteTextures(1, np.array(self.gl_tex,dtype=np.uint))

