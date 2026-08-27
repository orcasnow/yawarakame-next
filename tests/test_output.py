# Output tests verify both supported artifact formats.
from pathlib import Path

from yawarakame.models import (
    DialogueState,
    DialogueStatus,
    DialogueTurn,
    MatchResult,
    ResearchPacket,
    Source,
)
from yawarakame.output import OutputWriter


def test_output_writer_creates_markdown_and_json(tmp_path: Path) -> None:
    state = DialogueState(
        session_id="1234567890abcdef",
        topic="勝利した試合を振り返る",
        result=MatchResult.WIN,
        rounds=1,
        model="test-model",
        participants=["reporter", "ninja"],
        status=DialogueStatus.COMPLETED,
        research=ResearchPacket(
            search_required=True,
            decision_reason="test",
            sources=[Source(title="Example", url="https://example.com")],
        ),
        good_points=["前半の守備が安定していた"],
        improvement_points=["終盤の判断を改善したい"],
        turns=[
            DialogueTurn(
                turn_index=0,
                round_index=1,
                speaker_id="reporter",
                speaker_name="記者",
                label="記",
                phase="opening",
                intent="紹介する",
                text="振り返りましょう",
            )
        ],
    )
    writer = OutputWriter(tmp_path, state)
    writer.write(state)
    assert writer.json_path.exists()
    assert writer.markdown_path.exists()
    markdown = writer.markdown_path.read_text(encoding="utf-8")
    assert "**記**「振り返りましょう」" in markdown
    assert "[Example](https://example.com)" in markdown
    assert "## この試合の良かったところ" in markdown
    assert "- 前半の守備が安定していた" in markdown
    assert "## この試合の(´ε｀；)ｳｰﾝ…" in markdown
    assert "- 終盤の判断を改善したい" in markdown
