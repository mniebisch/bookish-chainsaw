import pytest

from mmfl.feature.light import geometric_object, player, quadratic


class TestConeBasics:
    source = geometric_object.Point(x=0, y=0)
    orientation = 0
    phi_max = 90
    phi_num = 3

    cone = player.Cone(
        source=source, orientation=orientation, phi_max=phi_max, phi_num=phi_num
    )

    def test_num_cone_lines(self) -> None:
        assert len(self.cone.traces) == self.phi_num

    def test_class_cone_line(self) -> None:
        assert all(isinstance(trace, player.Trace) for trace in self.cone.traces)

    def test_cone_lines(self) -> None:
        expected_traces = [
            geometric_object.AsymptoteX(x=0),
            geometric_object.Line(m=0, n=0),
            geometric_object.AsymptoteX(x=0),
        ]

        output_traces = [trace.line for trace in self.cone.traces]
        assert all(
            expected == pytest.approx(output)
            for expected, output in zip(expected_traces, output_traces)
        )


class TestConeLight:
    source = geometric_object.Point(x=0, y=0)
    orientation = 0
    phi_max = 90
    phi_num = 3

    cone = player.Cone(
        source=source, orientation=orientation, phi_max=phi_max, phi_num=phi_num
    )

    def test_shine_light(self) -> None:
        offense_players = [
            player.OffensePlayer(
                x_pos=4,
                y_pos=0,
                orientation=90,
                speed=10,
                acceleration=20,
                sphere_radius=2,
            ),
            player.OffensePlayer(
                x_pos=0,
                y_pos=-10,
                orientation=90,
                speed=10,
                acceleration=20,
                sphere_radius=1,
            ),
            player.OffensePlayer(
                x_pos=-2,
                y_pos=0,
                orientation=90,
                speed=10,
                acceleration=20,
                sphere_radius=1,
            ),
            player.OffensePlayer(
                x_pos=0,
                y_pos=2,
                orientation=270,
                speed=5,
                acceleration=2,
                sphere_radius=1,
            ),
        ]
        self.cone.shine_light(players=offense_players)

        expected_hits = [
            player.Hit(
                id=offense_players[1].id,
                point=geometric_object.Point(x=0, y=-9),
            ),
            player.Hit(
                id=offense_players[0].id,
                point=geometric_object.Point(x=2, y=0),
            ),
            player.Hit(
                id=offense_players[3].id,
                point=geometric_object.Point(x=0, y=1),
            ),
        ]

        output_hits = [trace.hit for trace in self.cone.traces]

        assert all(
            output == expected for output, expected in zip(output_hits, expected_hits)
        )


class TestDLinePlayer:
    def test_(self) -> None:
        defense_player = player.DLinePlayer(
            x_pos=1,
            y_pos=1,
            orientation=-90,
            speed=3,
            acceleration=1,
            phi_max=90,
            phi_num=3,
        )
        offense_players = [
            player.OffensePlayer(
                x_pos=1,
                y_pos=-8,
                orientation=90,
                speed=10,
                acceleration=20,
                sphere_radius=3,
            ),
        ]

        defense_player.rush(players=offense_players)
        expected_hits = [
            None,
            player.Hit(
                id=offense_players[0].id, point=geometric_object.Point(x=1, y=-5)
            ),
            None,
        ]
        output_hits = [trace.hit for trace in defense_player.cone.traces]
        assert all(
            expected == output for expected, output in zip(expected_hits, output_hits)
        )


class TestTrace:
    @pytest.fixture(name="offense_players")
    def create_offense_players(self) -> list[player.OffensePlayer]:
        offense_players = [
            player.OffensePlayer(
                x_pos=10,
                y_pos=1,
                orientation=270,
                speed=5,
                acceleration=2,
                sphere_radius=1,
            ),
            player.OffensePlayer(
                x_pos=-100,
                y_pos=1,
                orientation=90,
                speed=10,
                acceleration=20,
                sphere_radius=3,
            ),
            player.OffensePlayer(
                x_pos=-200,
                y_pos=1,
                orientation=90,
                speed=10,
                acceleration=20,
                sphere_radius=3,
            ),
        ]
        return offense_players

    @pytest.fixture(name="trace")
    def create_trace(self) -> player.Trace:
        trace = player.Trace(
            line=geometric_object.Line(m=0, n=1),
            orientation=180,
            origin=geometric_object.Point(x=0, y=1),
        )
        return trace

    def test_find_hit_expected_id(
        self, trace: player.Trace, offense_players: list[player.OffensePlayer]
    ) -> None:
        trace.find_hit(players=offense_players)
        assert trace.hit.id == offense_players[1].id

    def test_find_hit_expected_point(
        self, trace: player.Trace, offense_players: list[player.OffensePlayer]
    ) -> None:
        expected_point = geometric_object.Point(x=-97, y=1)
        trace.find_hit(players=offense_players)
        assert trace.hit.point == pytest.approx(expected_point)

    def test_find_hit_no_hit(
        self, trace: player.Trace, offense_players: list[player.OffensePlayer]
    ) -> None:
        trace.find_hit(players=offense_players[:1])
        assert trace.hit is None

    def test_filter_intersection_player_num(
        self, trace: player.Trace, offense_players: list[player.OffensePlayer]
    ) -> None:
        intersections: list[list[geometric_object.Point]] = [
            quadratic.calc_intersection(line=trace.line, circle=player.sphere)
            for player in offense_players
        ]
        _, filtered_players = trace.filter_intersections(
            intersections=intersections, elements=offense_players
        )
        assert len(filtered_players) == 2

    def test_filter_intersection_intersections_num(
        self, trace: player.Trace, offense_players: list[player.OffensePlayer]
    ) -> None:
        intersections: list[list[geometric_object.Point]] = [
            quadratic.calc_intersection(line=trace.line, circle=player.sphere)
            for player in offense_players
        ]
        filtered_intersections, _ = trace.filter_intersections(
            intersections=intersections, elements=offense_players
        )
        assert len(filtered_intersections) == 2

    def test_filter_intersection_num(
        self, trace: player.Trace, offense_players: list[player.OffensePlayer]
    ) -> None:
        intersections: list[list[geometric_object.Point]] = [
            quadratic.calc_intersection(line=trace.line, circle=player.sphere)
            for player in offense_players
        ]
        filtered_intersections, filtered_players = trace.filter_intersections(
            intersections=intersections, elements=offense_players
        )
        assert len(filtered_intersections) == len(filtered_players)
