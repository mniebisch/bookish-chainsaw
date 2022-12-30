import pytest

from mmfl.feature.light import geometric_object, utils


class TestFindNestedArgmin:
    @pytest.mark.parametrize(
        "xs, expected",
        [
            ([[1, 2], [1, 3], [0]], (2, 0)),
            ([[-1]], (0, 0)),
        ],
    )
    def test_find_min(
        self, xs: list[list[float | int]], expected: tuple[int, int]
    ) -> None:
        output = utils.find_nested_argmin(xs)
        assert expected == output

    @pytest.mark.parametrize(
        "xs, expected",
        [
            ([[1, 2], [], [3, 4]], (0, 0)),
            ([[]], (-1, -1)),
            ([[], []], (-1, -1)),
            ([], ()),
        ],
    )
    def test_empty_list(
        self, xs: list[list[float | int]], expected: tuple[int, int]
    ) -> None:
        output = utils.find_nested_argmin(xs)

        assert expected == output


class TestCalcOrientationSigns:
    @pytest.mark.parametrize(
        "deg, expected",
        [
            (0, (1, 0)),
            (45, (1, 1)),
            (90, (0, 1)),
            (-45, (1, -1)),
            (360 + 90 + 45, (-1, 1)),
        ],
    )
    def test_signs(self, deg: float, expected: tuple[int, int]) -> None:
        output = utils.calc_orientation_signs(deg=deg)
        assert output == expected


class TestCalcVectorSigns:
    @pytest.mark.parametrize(
        "src_x, src_y, dest_x, dest_y, expected",
        [(0, 0, 1, 1, (1, 1)), (0, 0, -1, 0, (-1, 0))],
    )
    def test_signs(
        self,
        src_x: float,
        src_y: float,
        dest_x: float,
        dest_y: float,
        expected: tuple[int, int],
    ) -> None:
        source = geometric_object.Point(x=src_x, y=src_y)
        destination = geometric_object.Point(x=dest_x, y=dest_y)

        output = utils.calc_vector_signs(source=source, destination=destination)

        assert expected == output
