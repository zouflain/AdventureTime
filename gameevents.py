import numpy as np
from PyQt6.QtGui import QCursor
class GameEvent:
    def __init__(self):
        pass


class ClickEvent(GameEvent):
    def __init__(self, pos: np.array):
        self.location = pos


class FixedTimeStepEvent(GameEvent):
    def __init__(self, game):
        super().__init__()


class RenderEvent(GameEvent):
    def __init__(self, coef: float):
        super().__init__()
        self.t = coef

