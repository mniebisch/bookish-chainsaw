import pytest

from mmfl.feature.light import geometric_object, quadratic


class TestNoIntersection:
    def test_length(self) -> None:
        circle = geometric_object.Circle(a=1, b=1, r=2)
        line = geometric_object.Line(m=-1, n=-2)

        output = quadratic.calc_intersection(line=line, circle=circle)

        assert len(output) == 0


class TestOneIntersection:
    circle = geometric_object.Circle(a=0, b=0, r=10)
    line = geometric_object.Line(m=0, n=10)

    def test_length(self) -> None:
        output = quadratic.calc_intersection(line=self.line, circle=self.circle)
        assert len(output) == 1

    def test_output_value(self) -> None:
        expected = [geometric_object.Point(x=0, y=10)]
        output = quadratic.calc_intersection(line=self.line, circle=self.circle)

        assert expected[0] == pytest.approx(output[0])


class TestTwoPointIntersection:
    circle = geometric_object.Circle(a=2, b=1, r=1)
    line = geometric_object.Line(m=0, n=1)

    def test_length(self) -> None:
        output = quadratic.calc_intersection(line=self.line, circle=self.circle)

        assert len(output) == 2

    def test_output_values(self) -> None:
        expected = [
            geometric_object.Point(x=1, y=1),
            geometric_object.Point(x=3, y=1),
        ]

        output = quadratic.calc_intersection(line=self.line, circle=self.circle)

        output_expected_match = zip(sorted(expected), sorted(output))
        elementwise_match = [
            expected == pytest.approx(output)
            for expected, output in output_expected_match
        ]
        assert all(elementwise_match)
