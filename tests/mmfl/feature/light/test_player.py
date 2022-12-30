import pytest

from mmfl.feature.light import geometric_object, player


class TestCone:
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
        ]
        return offense_players

    @pytest.fixture(name="trace")
    def create_trace(self, offense_players: list[player.OffensePlayer]) -> player.Trace:
        trace = player.Trace(line=geometric_object.Line(m=0, n=1))
        trace.find_hit(players=offense_players, origin=geometric_object.Point(x=0, y=1))
        return trace

    def test_find_hit_expected_id(
        self, trace: player.Trace, offense_players: list[player.OffensePlayer]
    ) -> None:
        assert trace.hit.id == offense_players[0].id

    def test_find_hit_expected_point(self, trace: player.Trace) -> None:
        expected_point = geometric_object.Point(x=9, y=1)
        assert trace.hit.point == pytest.approx(expected_point)
