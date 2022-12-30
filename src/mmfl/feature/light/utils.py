import numpy as np

__all__ = ["find_nested_argmin"]


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
