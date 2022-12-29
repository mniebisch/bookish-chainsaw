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
