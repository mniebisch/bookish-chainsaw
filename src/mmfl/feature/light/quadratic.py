import math

from mmfl.feature.light import geometric_object

__all__ = ["calc_intersection", "solve_quadratic"]


def solve_quadratic(a: float, b: float, c: float) -> list[float]:
    discriminant = b**2 - 4 * a * c

    if math.isclose(discriminant, 0):
        x = -b / (2 * a)
        return [x]
    elif discriminant > 0:
        x0 = (-b + math.sqrt(discriminant)) / (2 * a)
        x1 = (-b - math.sqrt(discriminant)) / (2 * a)
        return [x0, x1]
    else:
        return []


def _calc_asymptotex_intersection(
    asymptote: geometric_object.AsymptoteX, circle: geometric_object.Circle
) -> list[geometric_object.Point]:
    p = -2 * circle.b
    q = circle.b**2 + (asymptote.x - circle.a) ** 2 - circle.r**2

    ys = solve_quadratic(a=1, b=p, c=q)
    points = [geometric_object.Point(x=asymptote.x, y=y) for y in ys]
    return points


def _calc_line_intersection(
    line: geometric_object.Line, circle: geometric_object.Circle
) -> list[geometric_object.Point]:
    a = line.m**2 + 1
    b = 2 * line.m * line.n - 2 * circle.b * line.m - 2 * circle.a
    c = (circle.b - line.n) ** 2 + circle.a**2 - circle.r**2

    xs = solve_quadratic(a=a, b=b, c=c)
    points = [geometric_object.Point(x=x, y=line.calc_y(x=x)) for x in xs]
    return points


def calc_intersection(
    line: geometric_object.Line | geometric_object.AsymptoteX,
    circle: geometric_object.Circle,
) -> list[geometric_object.Point]:
    if isinstance(line, geometric_object.AsymptoteX):
        return _calc_asymptotex_intersection(asymptote=line, circle=circle)
    else:
        return _calc_line_intersection(line=line, circle=circle)
