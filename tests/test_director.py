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


def test_opening_builds_context_before_starting_lineup_review() -> None:
    director = Director(rounds=15, analyst_id="ninja")
    plans = [director.plan(index) for index in range(12)]

    assert [plan.phase for plan in plans] == ["opening"] * 12
    assert plans[0].intent.startswith("自己紹介")
    assert "問題提起" in plans[0].intent
    assert plans[1].intent.startswith("自己紹介")
    assert "問題提起" in plans[1].intent
    assert plans[2].intent.startswith("試合結果とスコア")
    assert plans[4].intent.startswith("結果にまつわる軽いボケ")
    assert plans[6].intent.startswith("結果にまつわる軽いボケ")
    assert plans[10].intent.startswith("スターティングメンバー")
    assert plans[11].intent.startswith("スターティングメンバーの構成")


def test_closing_uses_result_specific_fixed_last_three_lines() -> None:
    for analyst_id, expected in [
        ("ninja", ["おあとがよろしいようで", "それではまた次の記事でお会いいたしましょう", "ﾆﾝﾆﾝ"]),
        ("samurai", ["お後がよろしいようで", "それではまた次の記事でお会いいたしましょう", "成敗！（Say-Bye！)"]),
    ]:
        director = Director(rounds=15, analyst_id=analyst_id)
        plans = [director.plan(index) for index in range(30)]
        assert [plan.speaker_id for plan in plans[-3:]] == [analyst_id, "reporter", analyst_id]
        assert all(plan.intent == "固定の締め文をそのまま出力する" for plan in plans[-3:])
        assert expected[0] == ("おあとがよろしいようで" if analyst_id == "ninja" else "お後がよろしいようで")
