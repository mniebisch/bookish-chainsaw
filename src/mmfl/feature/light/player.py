from typing import Optional

from mmfl.feature.light import geometric_object


class Trace:
    def __init__(self, line: geometric_object.Line) -> None:
        self._line = line
        self._hit: Optional[geometric_object.Point] = None

    @property
    def line(self) -> geometric_object.Line:
        return self._line

    @property
    def hit(self) -> Optional[geometric_object.Point]:
        return self._hit

    @hit.setter
    def hit(self, value: geometric_object.Point) -> None:
        if value is None:
            raise ValueError
        self._hit = value

    def find_hit(self, players: list) -> None:
        raise NotImplementedError
