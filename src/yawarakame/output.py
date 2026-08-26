from __future__ import annotations

import re
from pathlib import Path

from yawarakame.models import DialogueState


def _safe_slug(topic: str, limit: int = 36) -> str:
    slug = re.sub(r"[^0-9A-Za-zぁ-んァ-ヶ一-龠ー]+", "-", topic).strip("-")
    return (slug[:limit].rstrip("-") or "dialogue")


class OutputWriter:
    def __init__(self, output_dir: Path, state: DialogueState) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        stem = f"{state.created_at.astimezone().strftime('%Y%m%d-%H%M%S')}-{_safe_slug(state.topic)}-{state.session_id[:8]}"
        self.json_path = output_dir / f"{stem}.json"
        self.markdown_path = output_dir / f"{stem}.md"

    def write(self, state: DialogueState) -> None:
        self.json_path.write_text(state.model_dump_json(indent=2), encoding="utf-8")
        self.markdown_path.write_text(self.render_markdown(state), encoding="utf-8")

    @staticmethod
    def render_markdown(state: DialogueState) -> str:
        lines = [
            f"# {state.topic}",
            "",
            f"- 結果区分: `{state.result.value}`",
            f"- 往復数: {state.rounds}",
            f"- モデル: `{state.model}`",
            f"- 状態: `{state.status.value}`",
            f"- Web Search: {'実行' if state.research.search_required else '未実行'}",
            f"- 判定理由: {state.research.decision_reason}",
            "",
            "## 対談",
            "",
        ]
        for turn in state.turns:
            lines.extend([f"**{turn.label}**「{turn.text}」", ""])

        if state.research.sources:
            lines.extend(["## 参考情報", ""])
            for source in state.research.sources:
                title = source.title or source.url
                lines.append(f"- [{title}]({source.url})")
            lines.append("")

        if state.error:
            lines.extend(["## 実行エラー", "", state.error, ""])
        return "\n".join(lines)

