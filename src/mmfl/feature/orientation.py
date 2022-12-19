import numpy as np
import pandas as pd

__all__ = ["calc_accumulated_orientation_change", "calc_orientation_deviation"]


def calc_accumulated_orientation_change(player_orientation: pd.Series) -> float:
    """
    Assume that player orientation is:
        - sorted in time
        - data of one player for a single play
    """
    differences = player_orientation.diff()
    # refactor?
    angle_differences = np.fmod(differences + 180, 360) - 180
    absolute_change = np.abs(angle_differences)
    accumulated_change = np.nansum(absolute_change)

    return accumulated_change


def calc_orientation_deviation(
    orientation_value: pd.Series, orientation_start: pd.Series
) -> pd.Series:
    orientation_recalculated = np.zeros_like(orientation_value)
    is_right = orientation_start == 90
    orientation_recalculated[is_right] = _calc_right_start(orientation_value[is_right])
    is_left = orientation_start == 270
    orientation_recalculated[is_left] = _calc_left_start(orientation_value[is_left])
    return pd.Series(orientation_recalculated, name="orientationDeviation")


def _calc_left_start(orientation: pd.Series) -> np.ndarray:
    # 270 deg
    orientation_recalculated = np.zeros_like(orientation)
    ind = orientation.between(90, 270)  # map to -180, 0
    orientation_recalculated[ind] = orientation[ind] - 270
    ind = orientation.between(270, 360)  # map to 0, 90
    orientation_recalculated[ind] = orientation[ind] - 270
    ind = orientation.between(0, 90)  # map to 90, 180
    orientation_recalculated[ind] = orientation[ind] + 90
    return orientation_recalculated


def _calc_right_start(orientation: pd.Series) -> np.ndarray:
    # 90 deg
    orientation_recalculated = np.zeros_like(orientation)
    ind = orientation.between(90, 270)  # map to 0, 180
    orientation_recalculated[ind] = orientation[ind] - 90
    ind = orientation.between(270, 360)  # map to -180, -90
    orientation_recalculated[ind] = orientation[ind] - (180 + 270)
    ind = orientation.between(0, 90)  # map to -90, 0
    orientation_recalculated[ind] = orientation[ind] - 90
    return orientation_recalculated
