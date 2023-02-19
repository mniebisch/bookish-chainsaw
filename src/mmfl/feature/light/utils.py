from typing import Any, Callable

import numpy as np

from mmfl.feature.light import geometric_object

__all__ = [
    "calc_orientation_signs",
    "calc_vector_signs",
    "find_nearest",
    "find_nearest_arg",
    "find_nested_argmin",
    "map_angle",
]


def _clean_zeros(xs: list[float]) -> list[float]:
    return [0 if np.isclose(x, 0) else x for x in xs]


def calc_orientation_signs(deg: float) -> tuple[int, int]:
    component_fs: list[Callable] = [np.cos, np.sin]

    trionometrics = [cf(np.deg2rad(deg)) for cf in component_fs]
    trionometrics = _clean_zeros(trionometrics)
    signs = np.sign(trionometrics)

    assert len(signs) == 2

    return signs[0], signs[1]


def calc_vector_signs(
    source: geometric_object.Point, destination: geometric_object.Point
) -> tuple[int, int]:
    differences = [destination.x - source.x, destination.y - source.y]
    differences = _clean_zeros(differences)
    signs = np.sign(differences)

    assert len(signs) == 2

    return signs[0], signs[1]


def find_nearest(array: np.ndarray, value: float) -> Any:
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def find_nearest_arg(array: np.ndarray, value: float) -> int:
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def find_nested_argmin(xs: list[list[float | int]]) -> tuple[int, int] | tuple:
    if not all(isinstance(x, list) for x in xs):
        raise ValueError

    if not xs:
        return ()

    nested_argmin: list[int] = [np.argmin(x) if not x == [] else np.nan for x in xs]

    if np.all(np.isnan(nested_argmin)):
        return (-1, -1)

    main_argmin: int = np.argmin(
        [
            x[x_argmin] if x_argmin is not np.nan else np.inf
            for x, x_argmin in zip(xs, nested_argmin)
        ]
    )

    return main_argmin, nested_argmin[main_argmin]


def create_angle_map(step: float = 0.01) -> tuple[np.ndarray, np.ndarray]:
    a = np.arange(0, 360, step=step)
    ind = find_nearest_arg(a, 90)
    b = np.roll(np.arange(360, 0, step=-step), ind)
    return a, b


def map_angle(nfl_angle: np.ndarray) -> np.ndarray:
    outside_range = np.logical_or(nfl_angle < 0, nfl_angle > 360)
    if np.any(outside_range):
        raise ValueError
    trigonometric_angle = 360 - nfl_angle + 90
    return trigonometric_angle % 360
