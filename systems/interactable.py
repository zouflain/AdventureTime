from PyQt6 import QtWidgets
from systems.basesystem import BaseSystem
from gameevents import *
import numpy as np


class ITreeAssembleEvent(GameEvent):
    def __init__(self, source: int, target: int):
        self.interactions = []
        self.source = source
        self.target = target


class ITree(QtWidgets.QWidget):
    def __init__(self, game, parent: QtWidgets.QWidget):
        super().__init__(parent)
        self.button_group = QtWidgets.QButtonGroup(parent=game)
        self.buttons = []
        self.radius = 100

    def form(self, game, loc: np.array, event: ITreeAssembleEvent):
        for old_button in self.buttons:
            self.button_group.removeButton(old_button)

        angle = 2*np.pi/len(event.interactions)
        for i, interaction in enumerate(event.interactions):
            button = QtWidgets.QPushButton(text=interaction, parent=self)
            self.buttons.append(button)
            self.button_group.addButton(button)
            theta = np.pi/2 + i*angle
            button.move(int(np.cos(theta)*self.radius)+self.radius, int(-np.sin(theta)*self.radius)+self.radius)

        self.move(loc[0]-self.radius, loc[1]-self.radius)
        self.show()
        print(loc)

class InteractionSystem(BaseSystem):
    def __init__(self):
        super().__init__()
        self.addListeners(
            {
                ClickEvent: self.onScreenClick
            }
        )
        self.itree = None

    def onScreenClick(self, game, event: ClickEvent):
        if self.itree is None:
            self.itree = ITree(game, game)
        itree_event = ITreeAssembleEvent(0,0)
        #game.eventBroadcast(itree_event)
        itree_event.interactions = ["This", "Is", "A", "Test", "!!!", "???"]
        self.itree.form(game, event.location, itree_event)
