import pytest

from psb.rules.settlement import expected_value_ah, settle_ah, split_line


def test_split_quarter_lines():
    assert split_line(-0.75) == (-1.0, -0.5)
    assert split_line(-0.25) == (-0.5, 0.0)
    assert split_line(0.25) == (0.0, 0.5)
    assert split_line(-1.0) == (-1.0, -1.0)
    assert split_line(-0.5) == (-0.5, -0.5)


@pytest.mark.parametrize(
    ("line", "for_", "against", "expected"),
    [
        (-0.75, 2, 0, 1.0),  # win both halves at odds 2.0
        (-0.75, 1, 0, 0.5),  # -0.5 half wins, -1.0 half pushes
        (-0.75, 1, 1, -1.0),  # both halves lose
        (-0.25, 1, 1, -0.5),  # 0.0 half pushes, -0.5 half loses
        (0.25, 1, 1, 0.5),  # 0.0 half pushes, +0.5 half wins
        (-1.0, 1, 0, 0.0),  # whole line push
    ],
)
def test_settle_ah(line, for_, against, expected):
    assert settle_ah(line, for_, against, odds=2.0) == pytest.approx(expected)


def test_ev_matches_design_doc_example():
    # Design doc worked example: home -0.75 at 2.00 with
    # P(win by 2+) = 28.7%, P(win by exactly 1) = 25.2%, P(draw or loss) = 46.1%.
    probs = {2: 0.287, 1: 0.252, 0: 0.461}
    assert expected_value_ah(-0.75, 2.0, probs) == pytest.approx(-0.048, abs=1e-3)
