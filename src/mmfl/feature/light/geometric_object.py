__all__ = ["AsymptoteX", "Circle", "Line", "Point"]

import dataclasses


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


@dataclasses.dataclass(frozen=True, order=True)
class Point:
    x: float
    y: float
