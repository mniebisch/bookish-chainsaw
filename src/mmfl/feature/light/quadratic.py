import math

from mmfl.feature.light import geometric_object


def calc_intersection(
    line: geometric_object.Line, circle: geometric_object.Circle
) -> list[geometric_object.Point]:
    a = line.m**2 + 1
    b = 2 * line.m * line.n - 2 * circle.b * line.m - 2 * circle.a
    c = (circle.b - line.n) ** 2 + circle.a**2 - circle.r**2

    discriminant = b**2 - 4 * a * c

    if math.isclose(discriminant, 0):
        x = -b / (2 * a)
        y = line.calc_y(x)
        return [geometric_object.Point(x, y)]
    elif discriminant > 0:
        x0 = (-b + math.sqrt(discriminant)) / (2 * a)
        y0 = line.calc_y(x0)
        x1 = (-b - math.sqrt(discriminant)) / (2 * a)
        y1 = line.calc_y(x1)
        return [geometric_object.Point(x0, y0), geometric_object.Point(x1, y1)]
    else:
        return []
