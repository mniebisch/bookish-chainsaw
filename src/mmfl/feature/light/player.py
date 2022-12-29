import dataclasses
import warnings
from typing import Optional

import numpy as np

from mmfl.feature.light import geometric_object

__all__ = ["Cone", "Trace"]

TraceElements = geometric_object.AsymptoteX | geometric_object.Line


@dataclasses.dataclass(frozen=True)
class Hit:
    id: int
    point: geometric_object.Point


class Trace:
    def __init__(self, line: TraceElements) -> None:
        self._line = line
        self._hit: Optional[Hit] = None

    @property
    def line(self) -> TraceElements:
        return self._line

    @property
    def hit(self) -> Optional[Hit]:
        return self._hit

    @hit.setter
    def hit(self, value: Hit) -> None:
        if value is None:
            raise ValueError
        self._hit = value

    def find_hit(self, players: list) -> None:
        raise NotImplementedError


class Cone:
    def __init__(
        self,
        source: geometric_object.Point,
        orientation: float,  # deg
        phi_max: float,  # deg
        phi_num: float,
    ) -> None:

        self._source = source
        self._orientation = orientation
        self._phi_max = phi_max
        self._phi_num = phi_num

        self._traces: list[Trace] = self._init_traces()

    @property
    def source(self) -> geometric_object.Point:
        return self._source

    @property
    def orientation(self) -> float:
        return self._orientation

    @property
    def phi_max(self) -> float:
        return self._phi_max

    @property
    def phi_num(self) -> float:
        return self._phi_num

    @property
    def traces(self) -> list[Trace]:
        return self._traces

    def _init_traces(self) -> list[Trace]:
        phis = np.linspace(
            start=self.orientation - self.phi_max,
            stop=self.orientation + self.phi_max,
            num=self.phi_num,
        )
        phis_x = np.cos(np.deg2rad(phis))
        phis_x = _clean_zeros(phis_x)
        phis_y = np.sin(np.deg2rad(phis))
        phis_y = _clean_zeros(phis_y)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            slopes = phis_y / phis_x

        traces = [
            Trace(_construct_trace(point=self.source, slope=slope)) for slope in slopes
        ]
        return traces


def _clean_zeros(x: np.ndarray) -> np.ndarray:
    return np.where(np.isclose(x, 0), 0, x)


def _construct_trace(
    point: geometric_object.Point, slope: float
) -> geometric_object.Line | geometric_object.AsymptoteX:
    if np.abs(slope) == np.inf:
        return geometric_object.AsymptoteX(point.x)
    else:
        intercept = point.y - slope * point.x
        return geometric_object.Line(m=slope, n=intercept)
