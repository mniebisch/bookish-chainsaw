import math
from typing import Optional

from mmfl.feature.light import geometric_object

__all__ = ["calc_intersection"]


def _calc_line_line_intersection(
    line1: geometric_object.Line, line2: geometric_object.Line
) -> Optional[geometric_object.Point]:
    n_diff = line1.n - line2.n
    m_diff = line2.m - line1.m
    if math.isclose(m_diff, 0):
        return None
    else:
        x = n_diff / m_diff
        y = line1.calc_y(x)
        return geometric_object.Point(x=x, y=y)


def _calc_line_asymptote_intersection(
    line: geometric_object.Line, asymptote: geometric_object.AsymptoteX
) -> Optional[geometric_object.Point]:
    y = asymptote.x * line.m + line.n
    x = line.calc_x(y=y)
    if x is None:  # line.m == 0
        x = asymptote.x

    return geometric_object.Point(x=x, y=y)


def _calc_asymptote_asymptote_intersection(
    asymptote1: geometric_object.AsymptoteX, asymptote2: geometric_object.AsymptoteX
) -> Optional[geometric_object.Point]:
    return None  # temporary solution


def calc_intersection(
    line1: geometric_object.Line | geometric_object.AsymptoteX,
    line2: geometric_object.Line | geometric_object.AsymptoteX,
) -> Optional[geometric_object.Point]:
    if isinstance(line1, geometric_object.Line) and isinstance(
        line2, geometric_object.Line
    ):
        return _calc_line_line_intersection(line1=line1, line2=line2)
    elif isinstance(line1, geometric_object.Line) and isinstance(
        line2, geometric_object.AsymptoteX
    ):
        return _calc_line_asymptote_intersection(line=line1, asymptote=line2)
    elif isinstance(line1, geometric_object.AsymptoteX) and isinstance(
        line2, geometric_object.Line
    ):
        return _calc_line_asymptote_intersection(line=line2, asymptote=line1)
    elif isinstance(line1, geometric_object.AsymptoteX) and isinstance(
        line2, geometric_object.AsymptoteX
    ):
        return _calc_asymptote_asymptote_intersection(
            asymptote1=line1, asymptote2=line2
        )
    else:
        raise ValueError
