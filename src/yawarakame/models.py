from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MatchResult(StrEnum):
    WIN = "win"
    DRAW = "draw"
    LOSS = "loss"


class DialogueStatus(StrEnum):
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"
    FAILED = "failed"


class RoleSpec(BaseModel):
    primary: str
    conversation_function: list[str]


class VoiceSpec(BaseModel):
    first_person: str
    sentence_endings: list[str]
    occasional_phrases: list[str]
    constraints: list[str]


class CharacterExample(BaseModel):
    situation: str
    text: str


class CharacterSpec(BaseModel):
    id: str
    name: str
    label: str
    role: RoleSpec
    worldview: list[str]
    voice: VoiceSpec
    relationships: dict[str, list[str]] = Field(default_factory=dict)
    examples: list[CharacterExample] = Field(default_factory=list)


class Source(BaseModel):
    title: str = ""
    url: str


class ResearchPacket(BaseModel):
    search_required: bool
    decision_reason: str
    summary: str = ""
    sources: list[Source] = Field(default_factory=list)
    response_id: str | None = None


class TurnPlan(BaseModel):
    turn_index: int
    round_index: int
    speaker_id: str
    phase: Literal["opening", "exploration", "challenge", "deepening", "synthesis", "closing"]
    intent: str


class DialogueTurn(BaseModel):
    turn_index: int
    round_index: int
    speaker_id: str
    speaker_name: str
    label: str
    phase: str
    intent: str
    text: str
    created_at: datetime = Field(default_factory=utc_now)


class DialogueState(BaseModel):
    session_id: str
    topic: str
    result: MatchResult
    rounds: int
    model: str
    participants: list[str]
    status: DialogueStatus = DialogueStatus.PLANNED
    research: ResearchPacket
    good_points: list[str] = Field(default_factory=list)
    improvement_points: list[str] = Field(default_factory=list)
    rolling_summary: str = ""
    summarized_turn_count: int = 0
    turns: list[DialogueTurn] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None
    error: str | None = None

