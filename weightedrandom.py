class WeightedRandom:
    def __init__(self):
        self.groups = []

    def addGroup(self, weight: int, option: any) -> None:
        self.groups.append((weight, option))

    def getRandom(self, game):
        total = 0
        for group in self.groups:
            total += group[0]

        value = game.random.randint(0,total)
        result = None
        for group in self.groups:
            value -= group[0]
            if value <= 0:
                result = group[1]
                break
        return result