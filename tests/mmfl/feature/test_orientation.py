import numpy as np
import pandas as pd
import pytest

from mmfl.feature import orientation


class TestCalcRightStart:
    @pytest.mark.parametrize(
        "orientation_value, expected_value",
        [(0, -90), (90, 0), (270, -180), (360, -90)],
    )
    def test_edge_cases(self, orientation_value: int, expected_value: int) -> None:
        input_value = pd.Series([orientation_value])
        expected_value = np.array([expected_value])
        output_value = (
            orientation._calc_right_start(  # pylint: disable=protected-access
                orientation=input_value
            )
        )
        np.testing.assert_equal(expected_value, output_value)

    @pytest.mark.parametrize(
        "orientation_value, expected_value",
        [(45, -45), (135, 45), (225, 135), (315, 315 - 180 - 270)],
    )
    def test_quater_center(self, orientation_value: int, expected_value: int) -> None:
        input_value = pd.Series([orientation_value])
        expected_value = np.array([expected_value])
        output_value = (
            orientation._calc_right_start(  # pylint: disable=protected-access
                orientation=input_value
            )
        )
        np.testing.assert_equal(expected_value, output_value)


class TestCalcLeftStart:
    @pytest.mark.parametrize(
        "orientation_value, expected_value",
        [(0, 90), (90, 180), (270, 0), (360, 90)],
    )
    def test_edge_cases(self, orientation_value: int, expected_value: int) -> None:
        input_value = pd.Series([orientation_value])
        expected_value = np.array([expected_value])
        output_value = orientation._calc_left_start(  # pylint: disable=protected-access
            orientation=input_value
        )
        np.testing.assert_equal(expected_value, output_value)
