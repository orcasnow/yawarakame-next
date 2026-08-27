from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from openai import OpenAI

from yawarakame.constants import AppDefaults
from yawarakame.actor import Actor, Summarizer
from yawarakame.characters import load_characters
from yawarakame.director import Director, participant_ids
from yawarakame.errors import safe_error_message
from yawarakame.models import (
    DialogueState,
    DialogueStatus,
    DialogueTurn,
    MatchResult,
    ResearchPacket,
)
from yawarakame.output import OutputWriter
from yawarakame.research import Researcher


class DialogueEngine:
    def __init__(
        self,
        client: OpenAI,
        model: str,
        output_dir: Path,
        safety_identifier: str | None = None,
    ) -> None:
        self.client = client
        self.model = model
        self.output_dir = output_dir
        self.characters = load_characters()
        self.researcher = Researcher(client, model, safety_identifier)
        self.actor = Actor(client, model, safety_identifier)
        self.summarizer = Summarizer(client, model, safety_identifier)

    def create_state(
        self,
        topic: str,
        result: MatchResult,
        rounds: int,
        search_required: bool,
        search_reason: str,
    ) -> DialogueState:
        participants = participant_ids(result)
        missing = [character_id for character_id in participants if character_id not in self.characters]
        if missing:
            raise ValueError(f"キャラクター定義が見つかりません: {', '.join(missing)}")
        return DialogueState(
            session_id=uuid4().hex,
            topic=topic,
            result=result,
            rounds=rounds,
            model=self.model,
            participants=participants,
            research=ResearchPacket(
                search_required=search_required,
                decision_reason=search_reason,
            ),
        )

    def run(self, state: DialogueState) -> tuple[DialogueState, OutputWriter]:
        writer = OutputWriter(self.output_dir, state)
        analyst_id = state.participants[1]
        director = Director(state.rounds, analyst_id)
        state.status = DialogueStatus.RUNNING
        writer.write(state)

        try:
            state.research = self.researcher.research(
                state.topic,
                state.research.search_required,
                state.research.decision_reason,
            )
            writer.write(state)

            for turn_index in range(state.rounds * 2):
                plan = director.plan(turn_index)
                if plan.phase == "closing" and not state.good_points and not state.improvement_points:
                    state.good_points, state.improvement_points = self.summarizer.review_points(state)
                    writer.write(state)
                character = self.characters[plan.speaker_id]
                other_id = analyst_id if plan.speaker_id == "reporter" else "reporter"
                fixed_texts = {
                    (analyst_id, state.rounds * 2 - 3): (
                        "おあとがよろしいようで" if analyst_id == "ninja" else "お後がよろしいようで"
                    ),
                    ("reporter", state.rounds * 2 - 2): "それではまた次の記事でお会いいたしましょう",
                    (analyst_id, state.rounds * 2 - 1): (
                        "ﾆﾝﾆﾝ" if analyst_id == "ninja" else "成敗！（Say-Bye！)"
                    ),
                }
                text = fixed_texts.get((plan.speaker_id, turn_index)) or self.actor.speak(
                    character, other_id, state, plan
                )
                turn = DialogueTurn(
                    turn_index=turn_index,
                    round_index=plan.round_index,
                    speaker_id=character.id,
                    speaker_name=character.name,
                    label=character.label,
                    phase=plan.phase,
                    intent=plan.intent,
                    text=text,
                )
                state.turns.append(turn)
                print(f"\n{character.label}「{text}」", flush=True)

                if len(state.turns) % AppDefaults.SUMMARY_INTERVAL == 0 and turn_index < state.rounds * 2 - 1:
                    state.rolling_summary = self.summarizer.update(state)
                    state.summarized_turn_count = len(state.turns)
                writer.write(state)

            state.status = DialogueStatus.COMPLETED
            state.completed_at = datetime.now(timezone.utc)
            writer.write(state)
            return state, writer
        except KeyboardInterrupt:
            state.status = DialogueStatus.INTERRUPTED
            state.completed_at = datetime.now(timezone.utc)
            state.error = "ユーザーにより中断されました"
            writer.write(state)
            raise
        except Exception as exc:
            state.status = DialogueStatus.FAILED
            state.completed_at = datetime.now(timezone.utc)
            state.error = f"{type(exc).__name__}: {safe_error_message(exc)}"
            writer.write(state)
            raise
