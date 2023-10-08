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
import pickle
import gzip
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

        self.camera = None
        self.meshes = {}
        self.shaders = {}
        self.textures = {}
        self.qimages = []  # Absolute hackish way to preserve qimage objects...

        self.timers = {}
        self.timers["render"] = QTimer()
        self.timers["render"].timeout.connect(self.update)
        self.timers["render"].setInterval(8)
        self.timers["render"].start()

        self.timers["fixed_step"] = QTimer()
        self.timers["fixed_step"].timeout.connect(self.fixedTimeStep)
        self.timers["fixed_step"].setInterval(50)
        self.timers["fixed_step"].start()

        self.current_room = 0

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
        glClearColor(0, 0, 0, 0)

        self.camera = Camera()

        self.loadShader("res/shaders/triangle")
        self.loadShader("res/shaders/sobeledge")

        # Load Textures (BEFORE models!)
        self.loadTextures()

        # Load models
        self.loadModels()

        ###OLD###
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
            self.textures[file] = Texture.fromFile(file)

    def loadModels(self):
        model_path = "res/models"
        for fname in [os.path.join(model_path, fname) for fname in os.listdir(model_path) if os.path.isfile(os.path.join(model_path, fname))]:
            if fname.endswith(".p3d.gz"):
                with gzip.open(fname) as file:
                    contents = pickle.load(file)
                    for mesh in contents.get("meshes", []):
                        self.meshes[mesh["info"]["name"]] = Mesh.fromDict(self, mesh)
                    for animation in contents.get("animations", []):
                        #Animation.fromDict(animation)
                        print(animation["meta"]["name"])




import cProfile, pstats

def main():
    format = QSurfaceFormat()
    format.setSamples(16)
    format.setSwapInterval(1)
    format.setSwapBehavior(QSurfaceFormat.SwapBehavior.DoubleBuffer)
    QSurfaceFormat.setDefaultFormat(format)

    app = QtWidgets.QApplication(sys.argv)
    game = Game()
    sys.exit(app.exec())

if __name__ == "__main__":
    cProfile.run("main()", filename="profile.prof")
    print(frames)
    stats = pstats.Stats("profile.prof")
    stats.sort_stats('tottime').print_stats(30)