
from PyQt6 import QtWidgets, QtOpenGLWidgets
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QSurfaceFormat
from systems.renderer import Renderer
from systems.interactable import InteractionSystem
from systems.listener import listenerComparator
from systems.camerasystem import CameraSystem
from texture import Texture
from gameevents import *
import sys
import os
from camera import Camera
from mesh import Mesh

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from intelligence import *
from levelgeneration import LevelGenerator
from components import *

frames = 0
class Game(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        # Config should eventually be loaded from file
        self.config = {
            "window": {
                "size": [1366,768],
                "resolution": [640, 480]
            }
        }

        # Configure QT
        wsize = self.getConfigProp("window", "size")
        self.resize(wsize[0], wsize[1])
        self.setWindowTitle("TESTING 3D!")
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)

        # Boot systems
        self.listeners = {}
        self.systems = [Renderer(self), InteractionSystem(), CameraSystem(self)]

        self.camera = Camera()
        self.meshes = {}
        self.shaders = {}
        self.textures = {}
        self.qimages = []  # Absolute hackish way to preserve qimage objects...

        self.timers = {}
        self.timers["render"] = QTimer()
        self.timers["render"].timeout.connect(self.update)
        self.timers["render"].setInterval(16)
        self.timers["render"].start()

        self.timers["fixed_step"] = QTimer()
        self.timers["fixed_step"].timeout.connect(self.fixedTimeStep)
        self.timers["fixed_step"].setInterval(50)
        self.timers["fixed_step"].start()

        self.show()


        #test code
        self.intelligence = Intelligence()
        self.intelligence.setActionSet(
            group="base",
            actions={
                "test": ActionTemplate(
                    target_type=TargetType([Renderable3D]),
                    weight=10.0,
                    considerations=[Consideration(), Consideration(), ConsiderRejectSelf()]
                )
            }
        )
        print(self.intelligence.chooseAction(100001, [100001, 100002]))

    def fixedTimeStep(self):
        self.eventBroadcast(FixedTimeStepEvent(self))

    def mousePressEvent(self, event):
        pos = event.pos()
        loc = np.array([pos.x(), pos.y()])
        #self.eventBroadcast(ClickEvent(loc))

    def closeEvent(self, event) -> None:
        for timer in self.timers.values():
            timer.stop()
        event.accept()

    def initializeGL(self) -> None:
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)
        '''glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glHint(GL_LINE_SMOOTH_HINT,GL_NICEST)'''
        glClearColor(0, 0, 0, 0)

        self.loadShader("res/shaders/triangle")
        self.loadShader("res/shaders/sobeledge")

        # Load Textures (BEFORE models!)
        self.loadTextures()

        # Load models
        model_path = "res/models"
        for file in [os.path.join(model_path, file) for file in os.listdir(model_path) if os.path.isfile(os.path.join(model_path, file))]:
            Mesh.fromFile(self,file)


        wres = self.getConfigProp("window", "resolution")
        self.camera.setOrtho(0,wres[0],0,wres[1],-10000,10000)


        #############TEST CODE###################
        level = LevelGenerator(25, 25)

        EntityManager.addComponents(
            components=[
                Renderable3D(meshes=["peasant_1"])
            ]
        )

        EntityManager.addComponents(
            components=[
                Renderable3D(
                    meshes=["Sphere"],
                    position=np.array((-200, -200, -50), dtype=np.float32)
                )
            ]
        )


        source = LightSource(
            np.array((-1000, -1000, 10000)),
            np.array((0.2, 0.2, 0.2)),
            np.array((0.5, 0.5, 0.5))
        )
        EntityManager.addComponents(
            components=[source]
        )

    def paintGL(self):
        timer = self.timers["fixed_step"]
        self.eventBroadcast(RenderEvent(timer.remainingTime()/timer.interval()))
        global frames
        frames += 1

    def addListener(self, etype: type, listener) -> None:
        if etype not in self.listeners:
            self.listeners[etype] = []
        listeners = self.listeners[etype]
        listeners.append(listener)
        self.listeners[etype] = sorted(listeners, key=cmp_to_key(listenerComparator))

    def dropListener(self, listener) -> None:
        for listeners in self.listeners.values():
            if listener in listeners:
                listeners.remove(listener)


    def eventBroadcast(self, event: GameEvent):
        for listener in self.listeners.get(type(event), []):
            if listener.execute(self, event):
                break


    def getConfigProp(self, cat: str, prop: str):
        result = None
        category = self.config.get(cat, None)
        if category:
            result = category if type(category) is not dict else category.get(prop, None)
        return result

    def getCamera(self) -> Camera:
        return self.camera

    def getMesh(self, name: str):
        return self.meshes.get(name, None)

    def getTexture(self, name: str) -> int:
        texture = self.textures.get(name, None)
        return 0 if not texture else texture.gl_tex

    def loadShader(self, name: str):
        try:
            with open(name+".vert") as vert_file:
                with open(name+".frag") as frag_file:
                    vert_src = vert_file.read()
                    frag_src = frag_file.read()
                    self.shaders[name] = compileProgram(
                        compileShader(vert_src, GL_VERTEX_SHADER),
                        compileShader(frag_src, GL_FRAGMENT_SHADER)
                    )
        except Exception as err:
            print(err)
            pass #should log this...


    def loadTextures(self) -> None:
        model_path = "res/textures"
        for file in [f"{model_path}/{file}" for file in os.listdir(model_path) if os.path.isfile(f"{model_path}/{file}")]:

            '''
            # Extremly painful QImage->np.array
            image = QImage(file)
            qbytes = QByteArray()
            buffer = QBuffer(qbytes)
            buffer.open(QIODevice.OpenModeFlag.WriteOnly)
            image.save(buffer, "PNG")
            arr = np.frombuffer(qbytes, np.uint8)

            # Now np.array->openGL
            tex = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D,tex)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width(), image.height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, arr)
            glGenerateMipmap(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, 0)

            self.textures[file] = tex
            '''

            '''
            image = QtOpenGL.QOpenGLTexture(QImage(file).mirrored())
            self.textures[file] = image.textureId()
            self.qimages.append(image)
            '''
            self.textures[file] = Texture.fromFile(file)


import cProfile, pstats

def main():
    format = QSurfaceFormat()
    format.setSamples(16)
    format.setSwapInterval(0)
    format.setSwapBehavior(QSurfaceFormat.SwapBehavior.DoubleBuffer)
    QSurfaceFormat.setDefaultFormat(format)

    app = QtWidgets.QApplication(sys.argv)
    game = Game()
    sys.exit(app.exec())

if __name__ == "__main__":
    '''
    context = self.context()
    surface = context.surface()
    context.setFormat(format)
    context.create()
    context.makeCurrent(surface)
    '''
    cProfile.run("main()", filename="profile.prof")
    print(frames)
    stats = pstats.Stats("profile.prof")
    stats.sort_stats('tottime').print_stats(30)