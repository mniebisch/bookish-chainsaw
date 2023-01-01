import numpy as np
from skimage import draw, morphology

from mmfl.feature.light import geometric_object, player, utils

# TODO calc all hits
# TODO calc possible signs for play direction?
# TODO how to handle play direction in general?
# TODO compute convex hull
# TODO compute intersection with QB asymptote for None hit traces


class Field:
    def __init__(
        self,
        oline_players: list[player.OffensePlayer],
        dline_players: list[player.DLinePlayer],
        quater_back: player.OffensePlayer,
        play_direction: str,
    ) -> None:
        self._oline_players = oline_players
        self._quater_back = quater_back
        self._dline_players = dline_players

        if play_direction not in ["left", "right"]:
            raise ValueError
        else:
            self._play_direction = play_direction

    @property
    def grid_resolution_factor(self) -> int:
        return 1

    @property
    def _buffer_factor(self) -> int:
        return 10

    @property
    def x_range(self) -> np.ndarray:
        return self._range(self.x_yards)

    @property
    def xlen(self) -> int:
        return len(self.x_range)

    @property
    def ylen(self) -> int:
        return len(self.y_range)

    @property
    def grid_shape(self) -> tuple[int, int]:
        return (self.ylen, self.xlen)

    def _range(self, yards: float) -> np.ndarray:
        yards = int(yards)
        buffer = int(yards / self._buffer_factor)
        return np.arange(
            start=0 - buffer,
            stop=yards + buffer,
            step=1 / self.grid_resolution_factor,
        )

    @property
    def y_range(self) -> np.ndarray:
        return self._range(self.y_yards)

    @property
    def oline_players(self) -> list[player.OffensePlayer]:
        return self._oline_players

    @property
    def quater_back(self) -> player.OffensePlayer:
        return self._quater_back

    @property
    def offense(self) -> list[player.OffensePlayer]:
        return self.oline_players + [self.quater_back]

    @property
    def dline_players(self) -> list[player.DLinePlayer]:
        return self._dline_players

    @property
    def play_direction(self) -> str:
        return self._play_direction

    @property
    def y_yards(self) -> float:
        return 53.3

    @property
    def x_yards(self) -> float:
        return 120.0

    @property
    def ymin(self) -> geometric_object.Line:
        return geometric_object.Line(m=0, n=0)

    @property
    def ymax(self) -> geometric_object.Line:
        return geometric_object.Line(m=0, n=self.y_yards)

    @property
    def xmin(self) -> geometric_object.AsymptoteX:
        return geometric_object.AsymptoteX(x=0)

    @property
    def xmax(self) -> geometric_object.AsymptoteX:
        return geometric_object.AsymptoteX(x=self.x_yards)

    def get_y_ind(self, value: float) -> int:
        return utils.find_nearest_arg(self.x_range, value)

    def get_x_ind(self, value: float) -> int:
        return utils.find_nearest_arg(self.y_range, value)

    def calc_player_interactions(self) -> None:
        for defense_player in self.dline_players:
            defense_player.rush(players=self.offense)

    def calc_convex_grid(self) -> np.ndarray:
        grid = np.zeros(self.grid_shape, dtype=int)

        for hull_player in self.offense:
            x_ind = self.get_x_ind(hull_player.x_pos)
            y_ind = self.get_y_ind(hull_player.y_pos)
            grid[y_ind, x_ind] = 1

        return morphology.convex_hull_image(grid)

    def draw_trace(self, trace: player.Trace) -> np.ndarray:
        if trace.hit is None:
            raise ValueError
        hit_point = trace.hit.point
        source_point = trace.origin

        hit_point_x = self.get_x_ind(hit_point.x)
        hit_point_y = self.get_y_ind(hit_point.y)

        source_point_x = self.get_x_ind(source_point.x)
        source_point_y = self.get_y_ind(source_point.y)

        rr, cc = draw.line(
            r0=source_point_y, c0=source_point_x, r1=hit_point_y, c1=hit_point_x
        )
        grid = np.zeros(self.grid_shape, dtype=int)
        grid[rr, cc] = 1
        return grid
