import dataclasses
import uuid
import warnings
from typing import Optional

import numpy as np

from mmfl.feature.light import geometric_object, quadratic, utils

__all__ = ["Cone", "Trace"]

TraceElements = geometric_object.AsymptoteX | geometric_object.Line


class Player:
    def __init__(
        self,
        x_pos: float,
        y_pos: float,
        orientation: float,
        speed: float,
        acceleration: float,
    ) -> None:
        self._x_pos = x_pos
        self._y_pos = y_pos
        self._orientation = orientation
        self._speed = speed
        self._acceleration = acceleration

        self._id = uuid.uuid4()

    @property
    def x_pos(self) -> float:
        return self._x_pos

    @property
    def y_pos(self) -> float:
        return self._y_pos

    @property
    def orientation(self) -> float:
        return self._orientation

    @property
    def speed(self) -> float:
        return self._speed

    @property
    def acceleration(self) -> float:
        return self._acceleration

    @property
    def id(self) -> uuid.UUID:
        return self._id


@dataclasses.dataclass(frozen=True)
class Hit:
    id: int
    point: geometric_object.Point


class OffensePlayer(Player):
    def __init__(
        self,
        x_pos: float,
        y_pos: float,
        orientation: float,
        speed: float,
        acceleration: float,
        sphere_radius: float,
    ) -> None:
        super().__init__(
            x_pos=x_pos,
            y_pos=y_pos,
            orientation=orientation,
            speed=speed,
            acceleration=acceleration,
        )

        self._sphere = geometric_object.Circle(
            a=self.x_pos, b=self.y_pos, r=sphere_radius
        )

    @property
    def sphere(self) -> geometric_object.Circle:
        return self._sphere


class Trace:
    # TODO add filter method based on orientation
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

    def find_hit(
        self, players: list[OffensePlayer], origin: geometric_object.Point
    ) -> None:
        # TODO create check if origin is on trace
        # TODO or better add to trace!
        intersections: list[list[geometric_object.Point]] = [
            quadratic.calc_intersection(line=self.line, circle=player.sphere)
            for player in players
        ]
        distances: list[list[float]] = [
            [np.linalg.norm(point.as_array() - origin.as_array()) for point in points]
            for points in intersections
        ]

        distance_min_ind = utils.find_nested_argmin(distances)
        # TODO don't like if need to know conditions following line. fix later
        if distance_min_ind or distance_min_ind != (-1, -1):
            hit_player = players[distance_min_ind[0]]
            hit_point = intersections[distance_min_ind[0]][distance_min_ind[1]]
            self.hit = Hit(id=hit_player.id, point=hit_point)


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


class DLinePlayer(Player):
    def __init__(
        self,
        x_pos: float,
        y_pos: float,
        orientation: float,
        speed: float,
        acceleration: float,
        phi_max: float,
        phi_num: float,
    ) -> None:
        super().__init__(
            x_pos=x_pos,
            y_pos=y_pos,
            orientation=orientation,
            speed=speed,
            acceleration=acceleration,
        )
        self._cone = Cone(
            source=geometric_object.Point(x=self.x_pos, y=self.y_pos),
            orientation=self.orientation,
            phi_max=phi_max,
            phi_num=phi_num,
        )

    @property
    def cone(self) -> Cone:
        return self._cone


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
