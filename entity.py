class EntityManager:
    next_id = 100000

    @classmethod
    def getNextID(cls) -> int:
        cls.next_id += 1
        return cls.next_id

    @classmethod
    def genIDs(cls, count: int) -> list[int]:
        ids = [i+cls.next_id for i in range(0, count)]
        cls.next_id += count
        return ids

    @classmethod
    def setNextID(cls, next_id) -> None:
        cls.next_id = next_id

    @classmethod
    def addComponents(cls, components: list = [], eid: int = None) -> int:
        if not eid:
            eid = cls.getNextID()

        for component in components:
            component.assign(eid)

        return eid

    @staticmethod
    def removeComponents(eid: int, components: list):
        for component in components:
            component.remove(eid)

    @staticmethod
    def findEntities(components: list) -> list[int]:
        entities = None
        for component in components:
            if not entities:
                entities = [eid for eid in component.entries]
            entities = [eid for eid in entities if eid in component.entries]
        return entities or []

    @staticmethod
    def hasComponents(eid: int, components: list) -> bool:
        has = True
        for component in components:
            if eid not in component.entries:
                has = False
                break
        return has

    @staticmethod
    def exportEntities(entities: list):
        for entity in entities:
            pass

