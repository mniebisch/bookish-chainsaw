import math

import pytest

from mmfl.feature.light import geometric_object, quadratic


class TestSolveQuadratic:
    @pytest.mark.parametrize(
        "a, b, c, expected",
        [
            (1, 1, 5, []),
            (1, 2, 1, [-1]),
            (2, 4, -4, [-1 + math.sqrt(3), -1 - math.sqrt(3)]),
        ],
    )
    def test_computation(
        self, a: float, b: float, c: float, expected: list[float]
    ) -> None:
        output = quadratic.solve_quadratic(a=a, b=b, c=c)

        assert sorted(expected) == pytest.approx(sorted(output))


class TestCalcIntersection:
    def test_asymptote(self) -> None:
        circle = geometric_object.Circle(a=1, b=1, r=1)
        asymptote = geometric_object.AsymptoteX(x=2)

        expected = [geometric_object.Point(x=2, y=1)]
        output = quadratic.calc_intersection(line=asymptote, circle=circle)

        assert expected[0] == pytest.approx(output[0])

    def test_line(self) -> None:
        circle = geometric_object.Circle(a=1, b=1, r=10)
        line = geometric_object.Line(m=0, n=11)

        expected = [geometric_object.Point(x=1, y=11)]
        output = quadratic.calc_intersection(line=line, circle=circle)

        assert expected[0] == pytest.approx(output[0])
