from systems.basesystem import BaseSystem
from systems.listener import Listener
from entity import EntityManager
from components import *
from OpenGL.GL import *
from gameevents import *
from model import *

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
        dynamic_renderables = [RenderableDynamic.get(entity) for entity in EntityManager.findEntities([RenderableDynamic])]

        self.computeBones(game, dynamic_renderables, event.t)
        self.bindLights()
        self.renderDynamicGroups(game, camera, dynamic_renderables)  # Dynamic objects
        #self.renderStaticGroups(game, camera, static_renderables)  # static objects dont need BONES!

        return False

    def computeBones(self, game, renderables, coef):
        glUseProgram(game.shaders.get("res/shaders/animation", 0))
        glUniform1f(0, coef)
        for renderable in renderables:
            armature = game.armatures.get(renderable.armature, None)
            if armature:
                glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, armature.bind_ssbo)
                if renderable.animation:
                    pass
                else: # use the bind pose as both previous and next frame
                    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, armature.bind_ssbo)
                    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 2, armature.bind_ssbo)
                glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 3, renderable.animation_ssbo)
                glDispatchCompute(20, 10, 1)
                glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
        glUseProgram(0)

    def bindLights(self):
        if not self.lights_ubo:
            arr = np.zeros(1, dtype=np.uint)
            glCreateBuffers(1, arr)
            self.lights_ubo = arr[0]
            glNamedBufferStorage(self.lights_ubo, 36*MAX_LIGHTS, None, GL_DYNAMIC_STORAGE_BIT | GL_MAP_READ_BIT)

        # Render 3D entities
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

    def renderDynamicGroups(self, game, camera, renderables):
        shader = game.shaders.get("res/shaders/mesh", 0)
        glUseProgram(shader)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, self.lights_ubo)
        glBindBufferBase(GL_UNIFORM_BUFFER, 2, camera.ubo)

        # Assemble Mesh groups
        mesh_groups = {}
        for renderable in renderables:
            for mesh in renderable.meshes:
                if mesh not in mesh_groups.keys():
                    mesh_groups[mesh] = []
                mesh_groups[mesh].append(renderable)

        # Render by mesh group
        for name, mesh_group in mesh_groups.items():
            mesh = game.meshes.get(name, None)
            if mesh:
                glBindTexture(GL_TEXTURE_2D, mesh.texture)
                mesh.preRender()
                for renderable in mesh_group:
                    glBindBufferBase(GL_UNIFORM_BUFFER, 0, renderable.ubo)
                    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 4, renderable.animation_ssbo)
                    mesh.render()

        #Clean up
        glBindTexture(GL_TEXTURE_2D, 0)
        glUseProgram(0)


