import pytest

# Director tests cover participant selection and the complete turn plan.
from yawarakame.director import Director, infer_result, participant_ids
from yawarakame.models import MatchResult


@pytest.mark.parametrize(
    ("topic", "expected"),
    [
        ("3-1で勝利した試合", MatchResult.WIN),
        ("悔しい敗戦を振り返る", MatchResult.LOSS),
        ("スコアレスドローだった", MatchResult.DRAW),
        ("今季の守備戦術について", None),
    ],
)
def test_infer_result(topic: str, expected: MatchResult | None) -> None:
    assert infer_result(topic) == expected


def test_loss_selects_samurai() -> None:
    assert participant_ids(MatchResult.LOSS) == ["reporter", "samurai"]


def test_win_and_draw_select_ninja() -> None:
    assert participant_ids(MatchResult.WIN) == ["reporter", "ninja"]
    assert participant_ids(MatchResult.DRAW) == ["reporter", "ninja"]


def test_fifteen_round_plan_has_thirty_turns_and_closes() -> None:
    director = Director(rounds=15, analyst_id="ninja")
    plans = [director.plan(index) for index in range(30)]
    assert len(plans) == 30
    assert plans[0].speaker_id == "reporter"
    assert plans[1].speaker_id == "ninja"
    assert plans[-2].phase == "synthesis"
    assert plans[-1].phase == "closing"
    assert plans[-1].speaker_id == "ninja"
