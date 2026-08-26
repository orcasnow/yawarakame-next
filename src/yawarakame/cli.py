from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from openai import OpenAI

from yawarakame.director import infer_result, participant_ids
from yawarakame.engine import DialogueEngine
from yawarakame.errors import safe_error_message
from yawarakame.models import MatchResult
from yawarakame.research import decide_web_search


SOCCER_MARKERS = re.compile(
    r"サッカー|フットボール|Jリーグ|J[123]|グランパス|日本代表|代表戦|ワールドカップ|"
    r"ACL|ACLE|天皇杯|ルヴァン|リーグ|試合|得点|失点|ゴール|選手|監督|フォーメーション|"
    r"プレス|ビルドアップ|カウンター|守備|攻撃|順位|勝利|敗戦|引き分け"
)


def is_soccer_topic(topic: str) -> bool:
    return bool(SOCCER_MARKERS.search(topic))


def _resolve_result(value: str, topic: str) -> MatchResult:
    if value != "auto":
        return MatchResult(value)
    inferred = infer_result(topic)
    if inferred:
        return inferred
    if sys.stdin.isatty():
        print("テーマから試合結果を判別できませんでした。")
        while True:
            answer = input("結果を入力してください [win/draw/loss]: ").strip().lower()
            try:
                return MatchResult(answer)
            except ValueError:
                print("win、draw、lossのいずれかを入力してください。")
    raise ValueError("試合結果を判別できません。--result win|draw|loss を指定してください")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="記者と忍者／侍によるサッカー対談を生成します")
    parser.add_argument("topic", nargs="?", help="対談テーマ。省略時は対話入力")
    parser.add_argument(
        "--result",
        choices=["auto", "win", "draw", "loss"],
        default="auto",
        help="試合結果（既定: auto）",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=int(os.getenv("YAWARAKAME_ROUNDS", "15")),
        help="往復数（既定: 15、発言数は2倍）",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OPENAI_MODEL", "gpt-5.6-terra"),
        help="OpenAIモデル",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(os.getenv("YAWARAKAME_OUTPUT_DIR", "output")),
        help="Markdown/JSON出力先",
    )
    search_group = parser.add_mutually_exclusive_group()
    search_group.add_argument("--search", dest="search_override", action="store_true")
    search_group.add_argument("--no-search", dest="search_override", action="store_false")
    parser.set_defaults(search_override=None)
    parser.add_argument("--plan-only", action="store_true", help="APIを呼ばず実行計画だけ表示")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    topic = (args.topic or input("対談テーマ: ")).strip()
    if not topic:
        parser.error("対談テーマを入力してください")
    if not is_soccer_topic(topic):
        parser.error("サッカー以外のテーマは扱えません。サッカーに関するテーマを指定してください")
    if not 1 <= args.rounds <= 30:
        parser.error("--rounds は1〜30で指定してください")

    try:
        result = _resolve_result(args.result, topic)
    except ValueError as exc:
        parser.error(str(exc))

    auto_search, reason = decide_web_search(topic)
    if args.search_override is None:
        search_required = auto_search
    else:
        search_required = args.search_override
        reason = "CLIオプションでWeb Searchを有効化" if search_required else "CLIオプションでWeb Searchを無効化"

    participants = participant_ids(result)
    print(f"テーマ: {topic}")
    print(f"結果: {result.value}")
    print(f"参加者: {', '.join(participants)}")
    print(f"往復数: {args.rounds}（{args.rounds * 2}発言）")
    print(f"Web Search: {'有効' if search_required else '無効'} / {reason}")
    print(f"モデル: {args.model}")
    if args.plan_only:
        return

    if not os.getenv("OPENAI_API_KEY"):
        parser.error("OPENAI_API_KEYが設定されていません")

    client = OpenAI(timeout=120.0, max_retries=3)
    engine = DialogueEngine(
        client=client,
        model=args.model,
        output_dir=args.output_dir,
        safety_identifier=os.getenv("OPENAI_SAFETY_IDENTIFIER"),
    )
    state = engine.create_state(topic, result, args.rounds, search_required, reason)
    try:
        _, writer = engine.run(state)
    except KeyboardInterrupt:
        print("\n対談を中断しました。途中結果は保存されています。", file=sys.stderr)
        raise SystemExit(130)
    except Exception as exc:
        print(f"\n実行に失敗しました: {safe_error_message(exc)}", file=sys.stderr)
        print("途中結果は出力先に保存されています。", file=sys.stderr)
        raise SystemExit(1)

    print("\n対談を保存しました。")
    print(f"Markdown: {writer.markdown_path.resolve()}")
    print(f"JSON: {writer.json_path.resolve()}")


if __name__ == "__main__":
    main()
