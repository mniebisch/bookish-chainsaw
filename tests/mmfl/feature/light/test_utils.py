import pytest

from mmfl.feature.light import utils


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
