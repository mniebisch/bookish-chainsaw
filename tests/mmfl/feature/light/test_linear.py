from typing import Optional

import pytest

from mmfl.feature.light import geometric_object, linear


class TestCalcIntersection:
    @pytest.mark.parametrize(
        "m1, n1, m2, n2, expected",
        [
            (1, 1, -1, 3, geometric_object.Point(x=1, y=2)),
            (0, 1, -1, 3, geometric_object.Point(x=2, y=1)),
            (-1, 3, 0, 1, geometric_object.Point(x=2, y=1)),
            (1, 1, 1, 10, None),
        ],
    )
    def test_line_line_intersection(
        self,
        m1: float,
        n1: float,
        m2: float,
        n2: float,
        expected: Optional[geometric_object.Point],
    ) -> None:
        line1 = geometric_object.Line(m=m1, n=n1)
        line2 = geometric_object.Line(m=m2, n=n2)
        output = linear.calc_intersection(line1=line1, line2=line2)
        assert expected == pytest.approx(output)

    def test_line_asymptote_intersection(self) -> None:
        line = geometric_object.Line(m=1, n=1)
        asymptote = geometric_object.AsymptoteX(x=3)
        expected = geometric_object.Point(x=3, y=4)
        output = linear.calc_intersection(line1=line, line2=asymptote)
        assert expected == pytest.approx(output)

    def test_asymptote_line_intersection(self) -> None:
        line = geometric_object.Line(m=1, n=1)
        asymptote = geometric_object.AsymptoteX(x=3)
        expected = geometric_object.Point(x=3, y=4)
        output = linear.calc_intersection(line1=asymptote, line2=line)
        assert expected == pytest.approx(output)

    def test_asymptote_asymptote_intersection(self) -> None:
        asymptote1 = geometric_object.AsymptoteX(x=-1)
        asymptote2 = geometric_object.AsymptoteX(x=1)
        output = linear.calc_intersection(line1=asymptote1, line2=asymptote2)
        assert output is None
