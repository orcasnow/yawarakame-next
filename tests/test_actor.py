from types import SimpleNamespace

from yawarakame.actor import Actor, _clip_speech, _normalize_speech, _sentence_count, _speech_limits
from yawarakame.constants import SpeechLimits
from yawarakame.models import CharacterSpec, DialogueState, MatchResult, ResearchPacket, TurnPlan


class FakeResponses:
    def __init__(self, outputs: list[str]) -> None:
        self.outputs = outputs
        self.requests: list[dict] = []

    def create(self, **request):
        self.requests.append(request)
        return SimpleNamespace(output_text=self.outputs.pop(0))


def _character() -> CharacterSpec:
    return CharacterSpec.model_validate(
        {
            "id": "ninja",
            "name": "忍者",
            "label": "忍",
            "role": {"primary": "分析", "conversation_function": ["答える"]},
            "worldview": ["冷静に見る"],
            "voice": {
                "first_person": "拙者",
                "sentence_endings": ["でござる"],
                "occasional_phrases": [],
                "constraints": [],
            },
            "relationships": {"reporter": ["質問に答える"]},
            "examples": [],
        }
    )


def _state() -> DialogueState:
    return DialogueState(
        session_id="test",
        topic="サッカーの試合を振り返る",
        result=MatchResult.WIN,
        rounds=2,
        model="test-model",
        participants=["reporter", "ninja"],
        research=ResearchPacket(search_required=False, decision_reason="test"),
    )


def test_speech_helpers() -> None:
    plan = TurnPlan(
        turn_index=1,
        round_index=1,
        speaker_id="ninja",
        phase="opening",
        intent="答える",
    )
    assert _speech_limits(plan) == (SpeechLimits.MAX_CHARACTERS, SpeechLimits.NORMAL_SENTENCES)
    assert _normalize_speech("一文目。\n\n  二文目。") == "一文目。 二文目。"
    assert _sentence_count("一文目。二文目？") == 2
    assert _sentence_count("本当！？そうでござる。") == 2
    assert _clip_speech("一文目。二文目。三文目。", 20, 2) == "一文目。二文目。"


def test_long_speech_is_compacted_once() -> None:
    responses = FakeResponses(["長い説明。" * 30, "要点は守備の距離感でござる。次もそこを見たい。"])
    client = SimpleNamespace(responses=responses)
    actor = Actor(client, "test-model")
    plan = TurnPlan(
        turn_index=1,
        round_index=1,
        speaker_id="ninja",
        phase="opening",
        intent="答える",
    )

    text = actor.speak(_character(), "reporter", _state(), plan)

    assert text == "要点は守備の距離感でござる。次もそこを見たい。"
    assert len(responses.requests) == 2
    assert f"{SpeechLimits.MAX_CHARACTERS}文字以内" in responses.requests[0]["instructions"]
    assert responses.requests[0]["max_output_tokens"] == 240
