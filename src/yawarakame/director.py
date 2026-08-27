from __future__ import annotations

from yawarakame.constants import DRAW_PATTERNS, LOSS_PATTERNS, WIN_PATTERNS
from yawarakame.models import MatchResult, TurnPlan


def infer_result(topic: str) -> MatchResult | None:
    if LOSS_PATTERNS.search(topic):
        return MatchResult.LOSS
    if DRAW_PATTERNS.search(topic):
        return MatchResult.DRAW
    if WIN_PATTERNS.search(topic):
        return MatchResult.WIN
    return None


def participant_ids(result: MatchResult) -> list[str]:
    analyst = "samurai" if result is MatchResult.LOSS else "ninja"
    return ["reporter", analyst]


REPORTER_MIDDLE_INTENTS = (
    "直前の分析で最も気になる一点だけを聞く",
    "短い反例を一つ示して問い直す",
    "ファン・サポーターが気になる一点を尋ねる",
    "結果と内容のどちらを重く見るか尋ねる",
    "相手チームの狙いを一つ尋ねる",
)

ANALYST_MIDDLE_INTENTS = (
    "直前の質問へ結論から答え、根拠を一つ示す",
    "反例を認めるか否かを短く答える",
    "個人とチーム構造のどちらが大きいか答える",
    "相手チームの良かった点を一つ挙げる",
    "既出内容を繰り返さず、新しい観察を一つ述べる",
)

OPENING_INTENTS = (
    (
        "自己紹介だけを行い、これから試合を振り返ることを伝える。問題提起や疑問提示はしない",
        "自己紹介だけを行う。試合結果への感想、分析、問題提起、疑問提示はしない",
    ),
    (
        "試合結果とスコアを簡潔に整理し、観戦者と前提を共有する",
        "結果を受け止め、勝敗または引き分けになった大きな流れを一言で述べる",
    ),
    (
        "結果にまつわる軽いボケや雑談を一つ入れ、対談の空気をほぐす（1）",
        "記者のボケや雑談に軽く反応し、結果についての感想を会話らしく返す（1）",
    ),
    (
        "結果にまつわる軽いボケや雑談を一つ入れ、観戦時の印象を共有する（2）",
        "記者の雑談を受け、結果に対する率直な感想をもう一つ返す（2）",
    ),
    (
        "結果にまつわる軽いボケや雑談を一つ入れ、試合を振り返る視点へ戻す（3）",
        "雑談に軽く応じたうえで、試合内容に目を向けるきっかけを示す（3）",
    ),
    (
        "スターティングメンバーを確認し、そのメンバー構成について最初の評論を求める",
        "スターティングメンバーの構成と、そこから見える狙いまたは気になる点を評論する",
    ),
)


class Director:
    def __init__(self, rounds: int, analyst_id: str) -> None:
        if rounds < 1:
            raise ValueError("往復数は1以上で指定してください")
        self.rounds = rounds
        self.analyst_id = analyst_id

    def plan(self, turn_index: int) -> TurnPlan:
        total_turns = self.rounds * 2
        if not 0 <= turn_index < total_turns:
            raise IndexError("発言番号が対談の範囲外です")

        round_index = turn_index // 2 + 1
        is_reporter = turn_index % 2 == 0
        speaker_id = "reporter" if is_reporter else self.analyst_id

        closing_start = max(1, self.rounds - 4)
        if round_index >= closing_start:
            phase = "synthesis" if is_reporter else "closing"
            final_turn = turn_index >= self.rounds * 2 - 3
            if final_turn:
                phase = "synthesis" if speaker_id == "reporter" else "closing"
                intent = "固定の締め文をそのまま出力する"
            else:
                intent = (
                    "議論の一致点と残る論点を短くまとめ、最後の見通しを尋ねる"
                    if is_reporter
                    else "今後の見通しを述べ、対談の締めに向けて話をまとめる"
                )
        elif round_index <= len(OPENING_INTENTS):
            phase = "opening"
            intent = OPENING_INTENTS[round_index - 1][0 if is_reporter else 1]
        elif round_index == self.rounds - 1 and self.rounds > 2:
            phase = "synthesis"
            intent = (
                "ここまでの主張を整理し、最終評価に必要な一点を確認する"
                if is_reporter
                else "一致点と相違点を踏まえて、現時点の総合評価を示す"
            )
        else:
            cycle_index = (round_index - 2) % len(REPORTER_MIDDLE_INTENTS)
            intent = (
                REPORTER_MIDDLE_INTENTS[cycle_index]
                if is_reporter
                else ANALYST_MIDDLE_INTENTS[cycle_index]
            )
            phase_cycle = ("exploration", "challenge", "deepening")
            phase = phase_cycle[(round_index - 2) % len(phase_cycle)]

        return TurnPlan(
            turn_index=turn_index,
            round_index=round_index,
            speaker_id=speaker_id,
            phase=phase,
            intent=intent,
        )
