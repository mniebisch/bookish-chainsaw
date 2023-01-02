__all__ = ["AsymptoteX", "Circle", "Line", "Point"]

import dataclasses
import math
from typing import Optional

import numpy as np


@dataclasses.dataclass(frozen=True)
class AsymptoteX:
    x: float


@dataclasses.dataclass(frozen=True)
class Circle:
    a: float
    b: float
    r: float


@dataclasses.dataclass(frozen=True)
class Line:
    m: float
    n: float

    def calc_y(self, x: float) -> float:
        return self.m * x + self.n

    def calc_x(self, y: float) -> Optional[float]:
        if math.isclose(self.m, 0):
            return None
        else:
            return (y - self.n) / self.m


@dataclasses.dataclass(frozen=True, order=True)
class Point:
    x: float
    y: float

    def as_array(self) -> np.ndarray:
        return np.array([self.x, self.y])
