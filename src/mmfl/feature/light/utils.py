from typing import Callable

import numpy as np

from mmfl.feature.light import geometric_object

__all__ = ["calc_orientation_signs", "calc_vector_signs", "find_nested_argmin"]


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
