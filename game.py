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
from random import Random
from camera import Camera
from model import Mesh, Armature
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

        self.camera = None #must initialize after openGL
        self.meshes = {}
        self.armatures = {}
        self.shaders = {}
        self.textures = {}
        self.qimages = []  # Absolute hackish way to preserve qimage objects...
        self.random = Random("Adventure time!")

        # Boot timers
        self.timers = {}
        self.timers["render"] = QTimer()
        self.timers["render"].timeout.connect(self.update)
        #self.timers["render"].setInterval(8)
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
                    target_type=TargetType([RenderableDynamic]),
                    weight=10.0,
                    considerations=[Consideration(), Consideration(), ConsiderRejectSelf()]
                )
            }
        )
        print(self.intelligence.chooseAction(100001, [100001, 100002]))

        from weightedrandom import WeightedRandom
        wr = WeightedRandom()
        for i in range(1, 11):
            wr.addGroup(10*i, f"{i} Group")

        for i in range(1, 6):
            print(wr.getRandom(self))

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

        self.loadShaders()
        self.loadTextures()  # Load Textures (BEFORE models!)
        self.loadModels()


        self.camera = Camera()
        wres = self.getConfigProp("window", "resolution")
        self.camera.setOrtho(0,wres[0],0,wres[1],-10000,10000)


        #############TEST CODE###################
        #level = LevelGenerator(10, 10)
        '''
        renderable = RenderableDynamic(
                    meshes=["Mage_Head", "Mage_ArmLeft", "Mage_ArmRight", "Mage_Body", "Mage_LegLeft", "2H_Staff", "Mage_Hat","Spellbook_open", "Mage_LegRight"], #
                    position=np.array((600, 0, 0), dtype=np.float32),
                    armature="Rig"
                )
        #renderable.animation = "Hit_A_Rig"
        renderable.animation = "Death_A_Rig"
        #renderable.animation = "T-Pose_Rig"
        #renderable.animation = "1H_Melee_Attack_Chop_Rig"
        print([animation for animation in self.armatures["Rig"].animations])
        EntityManager.addComponents(
            components=[
                renderable
            ]
        )

        renderable = RenderableDynamic(
            meshes=["Body"],
            position=np.array((600, 0, 0), dtype=np.float32),
            armature="Armature"
        )
        # renderable.animation = "Hit_A_Rig"
        print([animation for animation in self.armatures["Armature"].animations])
        EntityManager.addComponents(
            components=[
                renderable
            ]
        )
        '''

        source = LightSource(
            np.array((-1000, -1000, 10000)),
            np.array((0.5, 0.5, 0.5)),
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


    def eventBroadcast(self, event: GameEvent) -> None:
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

    def getMesh(self, name: str) -> Mesh:
        return self.meshes.get(name, None)

    def getTexture(self, name: str) -> int:
        texture = self.textures.get(name, None)
        return 0 if not texture else texture.gl_tex

    def loadShaders(self):
        shader_path = "res/shaders"
        for file in [f"{shader_path}/{file}" for file in os.listdir(shader_path) if os.path.isfile(f"{shader_path}/{file}")]:
            name = file[:-5]
            try:
                if file.endswith(".vert"):
                    with open(name+".vert") as vert_file:
                        with open(name+".frag") as frag_file:
                            vert_src = vert_file.read()
                            frag_src = frag_file.read()
                            self.shaders[name] = compileProgram(
                                compileShader(vert_src, GL_VERTEX_SHADER),
                                compileShader(frag_src, GL_FRAGMENT_SHADER)
                            )
                elif file.endswith(".comp"):
                    with open(file) as comp_file:
                        self.shaders[name] = compileProgram(
                            compileShader(comp_file.read(), GL_COMPUTE_SHADER)
                        )
            except Exception as err:
                print("Error loading shader:", err)



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
                    for armature in contents.get("armatures"):
                        animations = {}
                        for animation in armature.get("animations", []):
                            animations[animation["info"]["name"]] = Animation.fromDict(self, animation)
                        a_data = Armature(animations=animations, bind_list=armature["bones"])
                        self.armatures[armature["info"]["name"]] = a_data




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
