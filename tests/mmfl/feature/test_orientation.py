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

    @pytest.mark.parametrize(
        "orientation_value, expected_value",
        [(45, 135), (135, -135), (225, -45), (315, 45)],
    )
    def test_quater_center(self, orientation_value: int, expected_value: int) -> None:
        input_value = pd.Series([orientation_value])
        expected_value = np.array([expected_value])
        output_value = orientation._calc_left_start(  # pylint: disable=protected-access
            orientation=input_value
        )
        np.testing.assert_equal(expected_value, output_value)


class TestCalcOrientationDeviation:
    @pytest.mark.parametrize(
        "orientation_value, orientation_start_value, expected_value",
        [(45, 90, -45), (45, 270, 135)],
    )
    def test_computation(
        self, orientation_value: int, orientation_start_value: int, expected_value: int
    ) -> None:
        orientation_value = pd.Series([orientation_value])
        orientation_start_value = pd.Series([orientation_start_value])
        expected_value = pd.Series([expected_value], name="orientationDeviation")

        output_value = orientation.calc_orientation_deviation(
            orientation_value=orientation_value,
            orientation_start=orientation_start_value,
        )
        pd.testing.assert_series_equal(expected_value, output_value)


class TestCalcAccumulatedOrientationChange:
    def test_computation_simple(self) -> None:
        input_data = pd.Series([0, 10, 5, -15])
        expected_value = 35
        output_value = orientation.calc_accumulated_orientation_change(input_data)

        assert expected_value == pytest.approx(output_value)

    def test_computation_0_vs_360(self) -> None:
        input_data = pd.Series([2, 358])
        expected_value = 4

        output_value = orientation.calc_accumulated_orientation_change(input_data)

        assert expected_value == pytest.approx(output_value)
