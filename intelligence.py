from __future__ import annotations
from components import BaseComponent, CurrentRoom
from entity import EntityManager
from abc import abstractmethod
from functools import cmp_to_key
import numpy as np

ABORT_THRESHOLD = 1e-10


def responseCurve(shape: str, value: float, bounds: tuple[float, float], m: float, k: float, c: float, b: float) -> float:
    value = np.min(bounds[1], np.max(bounds[0], value))
    x = (value-bounds[0]) / (bounds[1]-bounds[0])
    y = x
    if shape == "linear" or shape == "quadratic":
        y = m*np.power(x+c,k)+b
    elif shape == "logarithmic":
        y = k/(1+np.power(1000*np.e*m,c-x))+b
    elif shape == "logistic":
        ln = np.log((x/k-c)/(1-x/k+c))/(np.log(np.e))
        y = ln/m+b
    elif shape == "sinoid":
        y = k*np.sin(m*x-c)+b
    return np.min(1.0, np.max(0.0, y))


def score_comparator(a, b) -> int:
    return int(round(b[1] - a[1]))


class TargetType:
    """Optimization class to prevent running EVERY consideration on EVERY entity given.
    Filters the given entity by type. MAYBBE a consideration in the future...
    Also, what about EXCLUDING enttiies with certain components?"""

    def __init__(self, components: list[BaseComponent]):
        self.required_components = components

    def isEntityTargetable(self, eid: int) -> bool:
        targetable = True
        for component in self.required_components:
            if eid not in component.entries:
                targetable = False
                break
        return targetable

    def getValidTargets(self, entities: list[int]) -> list[int]:
        return [entity for entity in entities if EntityManager.hasComponents(entity, self.required_components)]


class Consideration:
    """Basic class for evaluating potential actions."""

    def __init__(self, curve: str = "quadratic", params: tuple[float, float, float, float] = (1.0, 1.0, 0.0, 0.0)):
        self.curve = curve
        self.params = params

    @abstractmethod
    def evaluate(self, source: int, target: int) -> float:
        return 0.9


class ConsiderRejectSelf(Consideration):
    """Evaluates to zero if source == target else 1.0"""

    def evaluate(self, source: int, target: int) -> float:
        return float(target != source)


class ActionTemplate:

    def __init__(self, target_type: TargetType, weight: float, considerations: list[Consideration]):
        self.considerations = considerations
        self.target_type = target_type
        self.weight = weight

    def evaluate(self, source: int, entities: list[int]) -> list[(int, float, ActionTemplate)]:
        inv_len = 1.0/(len(self.considerations) or 1)
        targets = self.target_type.getValidTargets(entities)
        evaluations = []
        for target in targets:
            score = 1
            for consideration in self.considerations:
                score *= consideration.evaluate(source, target)
                if score < ABORT_THRESHOLD:
                    break
            score = np.power(score, inv_len)  # Normalize data
            evaluations.append((target, score * self.weight, self))
        print("Evaluations:", evaluations)
        return evaluations


class Intelligence:
    def __init__(self):
        self.action_sets = {}

    def setActionSet(self, group: str, actions: dict) -> None:
        self.action_sets[group] = actions

    def chooseAction(self, source: int, entities: list[int]) -> (int, ActionTemplate):
        actions = {}
        scores = []
        for action_set in self.action_sets.values():
            for name, action in action_set.items():
                actions[name] = action
        for action in actions.values():
            scores.extend(action.evaluate(source, entities))
        sorted_scores = sorted(scores, key=cmp_to_key(score_comparator))

        #For now, just do the top result. LATER pick random from any result within 10% of highest score
        return sorted_scores[0] if len(sorted_scores) > 0 else (0, None)
