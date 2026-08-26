from __future__ import annotations

import re

from yawarakame.models import MatchResult, TurnPlan


LOSS_PATTERNS = re.compile(r"敗戦|敗れ|負け(?:た|る|試合)?|惨敗|完敗|連敗")
DRAW_PATTERNS = re.compile(r"引き分け|ドロー|勝ち切れず|同点")
WIN_PATTERNS = re.compile(r"勝利|勝った|勝ち試合|快勝|辛勝|連勝")


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
    "直前の分析を短く整理し、根拠を具体化する質問をする",
    "まだ扱っていない別の可能性または反例を提示して問い直す",
    "ファン・サポーターが気になる点を示し、分析を求める",
    "結果と内容を分けて評価できるよう、論点を一段掘り下げる",
    "相手チーム側の狙いに視点を移し、説明を求める",
)

ANALYST_MIDDLE_INTENTS = (
    "直前の質問に答え、具体的な局面または戦術構造を一つ説明する",
    "反例を認めるべき部分は認め、自分の評価を修正または補強する",
    "個人のプレーとチーム全体の構造を分けて分析する",
    "相手チームの良かった点を含め、別の角度から分析する",
    "既出の説明を繰り返さず、次の論点になる観察を一つ加える",
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

        if round_index == 1:
            phase = "opening"
            intent = (
                "テーマを簡潔に紹介し、観戦者が最初に気になる疑問を一つ提示する"
                if is_reporter
                else "テーマへの第一印象と暫定的な結論を述べ、主要因を一つ示す"
            )
        elif round_index == self.rounds:
            phase = "synthesis" if is_reporter else "closing"
            intent = (
                "議論の一致点と残る論点を短くまとめ、最後の見通しを尋ねる"
                if is_reporter
                else "今後の見通しを述べ、キャラクターらしい挨拶で対談を締める"
            )
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

