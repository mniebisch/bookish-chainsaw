from typing import Optional

import numpy as np
from skimage import draw, morphology

from mmfl.feature.light import geometric_object, linear, player, utils

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
        return 10

    @property
    def _buffer_factor(self) -> int:
        return 10

    @property
    def x_range(self) -> np.ndarray:
        yards = int(self.x_yards)
        buffer = int(yards / self._buffer_factor)
        return np.arange(
            start=0 - buffer,
            stop=yards + buffer,
            step=1 / self.grid_resolution_factor,
        )

    @property
    def xlen(self) -> int:
        return len(self.x_range)

    @property
    def ylen(self) -> int:
        return len(self.y_range)

    @property
    def grid_shape(self) -> tuple[int, int]:
        return (self.ylen, self.xlen)

    @property
    def y_range(self) -> np.ndarray:
        yards = int(self.y_yards)
        buffer = int(yards / self._buffer_factor)
        return np.arange(
            start=yards + buffer,
            stop=0 - buffer,
            step=-1 / self.grid_resolution_factor,
        )

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

    @property
    def field_borders(
        self,
    ) -> tuple[
        geometric_object.Line,
        geometric_object.AsymptoteX,
        geometric_object.Line,
        geometric_object.AsymptoteX,
    ]:
        return (self.ymax, self.xmax, self.ymin, self.xmin)

    def get_y_ind(self, value: float) -> int:
        """
        Drawing utility.
        Map actual field position (value) to position on to be drawn grid.
        Difference due to `self.grid_resolution_factor`.
        """
        return utils.find_nearest_arg(self.y_range, value)

    def get_x_ind(self, value: float) -> int:
        """
        Drawing utility.
        Map actual field position (value) to position on to be drawn grid.
        Difference due to `self.grid_resolution_factor`.
        """
        return utils.find_nearest_arg(self.x_range, value)

    def calc_player_interactions(self) -> None:
        for defense_player in self.dline_players:
            defense_player.rush(players=self.offense)

    def calc_convex_grid(self) -> np.ndarray:
        grid = np.zeros(self.grid_shape, dtype=int)

        for hull_player in self.dline_players + [self.quater_back]:
            x_ind = self.get_x_ind(hull_player.x_pos)
            y_ind = self.get_y_ind(hull_player.y_pos)
            grid[y_ind, x_ind] = 1

        return morphology.convex_hull_image(grid)

    def default_pocket(self) -> np.ndarray:
        grid = np.zeros(self.grid_shape, dtype=int)
        offense_players = [
            (offense_player.x_pos, offense_player.y_pos)
            for offense_player in self.offense
        ]
        offense_players = np.array(offense_players)
        x_min = np.min(offense_players[:, 0])
        x_max = np.max(offense_players[:, 0])
        y_min = np.min(offense_players[:, 1])
        y_max = np.max(offense_players[:, 1])

        top_left = (x_min, y_max)
        top_right = (x_max, y_max)
        bottom_right = (x_max, y_min)
        bottom_left = (x_min, y_min)

        polygon = [top_left, top_right, bottom_right, bottom_left]
        x_values = [self.get_x_ind(x) for x, _ in polygon]
        y_values = [self.get_y_ind(y) for _, y in polygon]
        rr, cc = draw.polygon(r=y_values, c=x_values)
        grid[rr, cc] = 1
        return grid

    def calc_pocket_components(self) -> np.ndarray:
        import matplotlib.pyplot as plt

        default_pocket = self.default_pocket()
        defense_cones = [
            self.draw_cone(defense_player) for defense_player in self.dline_players
        ]
        fig, axs = plt.subplots(len(defense_cones))
        for i, img in enumerate(defense_cones):
            axs[i].imshow(img > 0)
        plt.show()
        defense_cones = np.stack(defense_cones)
        defense_light = np.sum(defense_cones, axis=0)
        defense_light = defense_light > 0
        pocket_light = np.logical_and(defense_light, default_pocket)
        actual_pocket = default_pocket - np.logical_not(pocket_light).astype(int)
        actual_pocket = np.where(np.isclose(actual_pocket, 0), 1, 0)
        return actual_pocket

    def draw_trace(self, trace: player.Trace) -> np.ndarray:
        if trace.hit is None:
            raise ValueError
        hit_point = trace.hit.point
        source_point = trace.origin

        return self.draw_line(point1=hit_point, point2=source_point)

    def draw_line(
        self, point1: geometric_object.Point, point2: geometric_object.Point
    ) -> np.ndarray:
        hit_point_x = self.get_x_ind(point1.x)
        hit_point_y = self.get_y_ind(point1.y)

        source_point_x = self.get_x_ind(point2.x)
        source_point_y = self.get_y_ind(point2.y)

        rr, cc = draw.line(
            r0=source_point_y, c0=source_point_x, r1=hit_point_y, c1=hit_point_x
        )
        grid = np.zeros(self.grid_shape, dtype=int)
        grid[rr, cc] = 1
        return grid

    def find_hit(self, trace: player.Trace) -> geometric_object.Point:
        intersections: list[Optional[geometric_object.Point]] = [
            linear.calc_intersection(line1=border, line2=trace.line)
            for border in self.field_borders
        ]
        intersections: list[geometric_object.Point] = [
            intersection for intersection in intersections if intersection is not None
        ]
        intersections, _ = trace.filter_intersections(
            intersections=[[intersection] for intersection in intersections],
            elements=list(range(len(intersections))),
        )
        intersections = [intersection[0] for intersection in intersections]
        distances: list[float] = [
            np.linalg.norm(point.as_array() - trace.origin.as_array())
            for point in intersections
        ]
        distance_argmin = np.argmin(distances)
        return intersections[distance_argmin]

    def draw_cone(self, defense_player: player.DLinePlayer) -> np.ndarray:
        trace_imgs = []
        for trace in defense_player.cone.traces:
            if trace.hit is not None:
                trace_img = self.draw_trace(trace=trace)
                trace_imgs.append(trace_img)
            else:
                border_intersection: geometric_object.Point = self.find_hit(trace=trace)
                trace_img = self.draw_line(
                    point1=border_intersection, point2=trace.origin
                )
                trace_imgs.append(trace_img)
        trace_imgs = np.stack(trace_imgs)
        return np.sum(trace_imgs, axis=0)
