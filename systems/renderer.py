from systems.basesystem import BaseSystem
from systems.listener import Listener
from entity import EntityManager
from components import *
from OpenGL.GL import *
from OpenGL import GLU
from gameevents import *
from components import Renderable, Renderable3D, WorldPosition
from mesh import Mesh

MAX_LIGHTS = 100


class Renderer(BaseSystem):
    def __init__(self, game):
        super().__init__()
        self.listener = Listener(100, self.renderScene)
        game.addListener(RenderEvent, self.listener)
        self.lights_ubo = 0  # must be done later, due to openGL not yet being initialized

    def renderScene(self, game, event: RenderEvent) -> bool:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        camera = game.getCamera()
        camera.interpolate(event.t)
        if not self.lights_ubo:
            arr = np.zeros(1, dtype=np.uint)
            glCreateBuffers(1, arr)
            self.lights_ubo = arr[0]
            glNamedBufferStorage(self.lights_ubo, 36*MAX_LIGHTS, None, GL_DYNAMIC_STORAGE_BIT | GL_MAP_READ_BIT)

        # Render 3D entities
        entities = EntityManager.findEntities([Renderable3D])
        lights = [LightSource.get(light) for light in EntityManager.findEntities([LightSource])][:MAX_LIGHTS]
        light_data = np.array(
            [
                (light.diffuse, light.ambient, light.position) for light in lights
            ],
            dtype=np.dtype(
                [
                    ("dif", (np.float32, 3)),
                    ("amb", (np.float32, 3)),
                    ("pos", (np.float32, 3))
                ]
            )
        )
        glNamedBufferSubData(self.lights_ubo, 0, light_data.nbytes, light_data)

        ###NEW CODE###
        shader = game.shaders.get("res/shaders/triangle", 0)
        glUseProgram(shader)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, self.lights_ubo)
        glBindBufferBase(GL_UNIFORM_BUFFER, 2, camera.ubo)

        # Assemble Mesh groups
        mesh_groups = {}
        for entity in entities:
            renderable = Renderable3D.get(entity)
            for mesh in renderable.meshes:
                if mesh not in mesh_groups.keys():
                    mesh_groups[mesh] = []
                mesh_groups[mesh].append(renderable.ubo)

        # Render by mesh group
        for name, mesh_group in mesh_groups.items():
            mesh = game.meshes.get(name, None)
            if mesh:
                glBindTexture(GL_TEXTURE_2D, mesh.texture)
                mesh.preRender()
                for model_ubo in mesh_group:
                    glBindBufferBase(GL_UNIFORM_BUFFER, 0, model_ubo)
                    mesh.render()

        #Clean up
        Mesh.postRender()
        glUseProgram(0)
        glBindTexture(GL_TEXTURE_2D, 0)

        return False


