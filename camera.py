from OpenGL.GL import *
import numpy as np


def makeTranslation(x: float, y: float, z: float) -> np.array:
    return np.array(
        (
            (1, 0, 0, -x),
            (0, 1, 0, -y),
            (0, 0, 1, -z),
            (0, 0, 0, 1)
        ),
        dtype=np.float32
    )


class Camera:

    identity = np.array(
        (
            (1, 0, 0, 0),
            (0, 1, 0, 0),
            (0, 0, 1, 0),
            (0, 0, 0, 1)
        ),
        dtype=np.float32
    )

    def __init__(self, perspective: np.array = None, ortho: np.array = None, view: np.array = None):
        self.perspective = np.identity(4,dtype=np.float32) if perspective is None else perspective
        self.ortho = np.identity(4,dtype=np.float32) if ortho is None else ortho
        self.view = np.identity(4,dtype=np.float32) if view is None else view
        self.center = np.zeros(3, dtype=np.float32)
        self.desired_center = np.zeros(3, dtype=np.float32)
        self.source_center = np.zeros(3, dtype=np.float32)
        self.distance = 1
        self.theta = np.pi/4

        # Build UBO
        arr = np.zeros(1, dtype=np.uint)
        glCreateBuffers(1, arr)
        self.ubo = arr[0]
        matrix_arr = np.array(
            (self.ortho, self.view),
            dtype=np.float32
        )
        glNamedBufferStorage(self.ubo, matrix_arr.nbytes, matrix_arr, GL_DYNAMIC_STORAGE_BIT | GL_MAP_READ_BIT)

        self.reconstruct()

    def reconstruct(self):
        self.isometricLook(
            x=self.center[0],
            y=self.center[1],
            z=self.center[2],
            d=self.distance,
            theta=self.theta
        )
        matrix_arr = np.array(
            (self.ortho, self.view),
            dtype=np.float32
        )
        glNamedBufferSubData(self.ubo, 0, matrix_arr.nbytes, matrix_arr)

    def pan(self, x: float, y: float, z: float):
        self.source_center = self.desired_center
        self.desired_center[0] = self.source_center[0]+x
        self.desired_center[1] = self.source_center[1]+y
        self.desired_center[2] = self.source_center[2]+z

    def interpolate(self, t: float):
        for i in range(0, 3):
            self.center[i] = self.source_center[i]*t+self.desired_center[i]*(1-t)
        self.reconstruct()


    def setOrtho(self, left: float, right: float, bottom: float, top: float, near: float, far: float) -> np.array:
        self.ortho = np.array(
            (
                (2/(right-left), 0, 0, -(right+left)/(right-left)),
                (0, 2/(top-bottom), 0, -(top+bottom)/(top-bottom)),
                (0, 0, -2/(far-near), -(far+near)/(far-near)),
                (0, 0, 0, 1)
            )
        )

    def setPerspective(self, fovy: float, aspect: float, near: float, far: float):
        f = np.cos(fovy/2)/np.sin(fovy/2)
        self.perspective = np.array(
            (
                (f/aspect, 0, 0, 0),
                (0, f, 0, 0),
                (0, 0, (far+near)/(near-far), 2*far*near/(near-far)),
                (0, 0, -1, 0)
            ),
            dtype=np.float32
        )

    def setView(self, eye_x: float, eye_y: float, eye_z: float, center_x: float, center_y: float, center_z: float,
               up_x: float, up_y: float, up_z: float) -> None:
        forward = np.array(
            (center_x - eye_x, center_y - eye_y, center_z - eye_z),
            dtype=np.float32
        )
        forward = forward/(np.linalg.norm(forward) or 1)
        up = np.array(
            (up_x, up_y, up_z),
            dtype=np.float32
        )
        up = up/(np.linalg.norm(up) or 1)
        s = np.cross(forward, up)
        u = np.cross(s/(np.linalg.norm(s) or 1), forward)

        self.view = np.array(
            (
                (s[0], s[1], s[2], 0),
                (u[0], u[1], u[2], 0),
                (-forward[0], -forward[1], -forward[2], 0),
                (0, 0, 0, 1)
            )
        )
        '''
        translation = np.array(
            (
                (1, 0, 0, -eye_x),
                (0, 1, 0, -eye_y),
                (0, 0, 1, -eye_z),
                (0, 0, 0, 1)
            )
        )
        self.view = np.matmul(view, translation)
        '''
        self.translateView(eye_x,eye_y,eye_z)

    def translateView(self, x: float, y: float, z: float):
        self.view = np.matmul(makeTranslation(x,y,z), self.view)

    def isometricLook(self, x: float, y: float, z: float, d: float, phi: float = np.pi/6, theta: float = np.pi/4):
        iz = np.sin(phi)*d
        ix = x-np.sin(theta)*d
        iy = y-np.cos(theta)*d
        self.setView(ix, iy, iz, x, y, z, 0, 0, 1)

