class BaseSystem:
    def __init__(self):
        self.listeners = {}

    def addListeners(self, listeners: dict) -> None:
        for cls, listener in listeners.items():
            self.listeners[cls] = listener

    def respond(self, game, event) -> bool:
        cls = type(event)
        return False if cls not in self.listeners else self.listeners[cls](game, event)
