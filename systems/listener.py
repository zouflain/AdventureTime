from gameevents import GameEvent


class Listener:
    def __init__(self, priority: int, callback: callable, **kwargs):
        self.priority = priority
        self.callback = callback
        self.kwargs = kwargs

    def execute(self, game, event: GameEvent) -> bool:
        return self.callback(game=game, event=event, **self.kwargs)


def listenerComparator(a: Listener, b: Listener) -> int:
    return a.priority - b.priority