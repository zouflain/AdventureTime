from systems.basesystem import BaseSystem
from systems.listener import Listener
from gameevents import *
from camera import Camera

class CameraSystem(BaseSystem):
    WINDOW_SCROLL_MARGIN = 50
    WINDOW_SCROLL_SPEED = 50
    def __init__(self, game):
        super().__init__()
        self.listener = Listener(100, self.fixedTimeStep)
        game.addListener(FixedTimeStepEvent, self.listener)

    def fixedTimeStep(self, game, event: FixedTimeStepEvent) -> bool:
        pos = game.mapFromGlobal(QCursor().pos())
        wres = game.getConfigProp("window","size")
        mouse_pos = np.array(
            [
                np.clip(pos.x(), 0, wres[0]),
                np.clip(pos.y(), 0, wres[1])
            ]
        )
        theta = game.camera.theta
        change = np.zeros(2, dtype=np.float32)
        if mouse_pos[0] <= self.WINDOW_SCROLL_MARGIN:
            change[0] = self.WINDOW_SCROLL_SPEED*((self.WINDOW_SCROLL_MARGIN-mouse_pos[0])/self.WINDOW_SCROLL_MARGIN)
        elif mouse_pos[0] >= wres[0]-self.WINDOW_SCROLL_MARGIN:
            change[0] = -self.WINDOW_SCROLL_SPEED*(1-((wres[0]-mouse_pos[0])/self.WINDOW_SCROLL_MARGIN))

        if mouse_pos[1] <= self.WINDOW_SCROLL_MARGIN:
            change[1] = -self.WINDOW_SCROLL_SPEED*((self.WINDOW_SCROLL_MARGIN-mouse_pos[1])/self.WINDOW_SCROLL_MARGIN)
        elif mouse_pos[1] >= wres[1] - self.WINDOW_SCROLL_MARGIN:
            change[1] = self.WINDOW_SCROLL_SPEED*(1-((wres[1]-mouse_pos[1])/self.WINDOW_SCROLL_MARGIN))

        game.camera.pan(-np.cos(theta)*change[0], -np.sin(theta)*change[1], 0)
        return False
