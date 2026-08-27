from __future__ import annotations

import re


class AppDefaults:
    DEFAULT_RESULT = "auto"
    DEFAULT_ROUNDS = 30
    MIN_ROUNDS = 1
    MAX_ROUNDS = 30
    DEFAULT_MODEL = "gpt-5.6-terra"
    DEFAULT_OUTPUT_DIR = "output"
    OUTPUT_SLUG_LIMIT = 36
    TRANSCRIPT_LIMIT = 10
    SUMMARY_INTERVAL = 6


class EnvironmentVariables:
    API_KEY = "OPENAI_API_KEY"
    MODEL = "OPENAI_MODEL"
    ROUNDS = "YAWARAKAME_ROUNDS"
    OUTPUT_DIR = "YAWARAKAME_OUTPUT_DIR"
    SAFETY_IDENTIFIER = "OPENAI_SAFETY_IDENTIFIER"


class ApiLimits:
    TIMEOUT_SECONDS = 120.0
    MAX_RETRIES = 3
    RESEARCH_MAX_TOOL_CALLS = 3
    ACTOR_MAX_OUTPUT_TOKENS = 240
    COMPACTION_MAX_OUTPUT_TOKENS = 180
    SUMMARY_MAX_OUTPUT_TOKENS = 400
    REVIEW_MAX_OUTPUT_TOKENS = 300


class SpeechLimits:
    MAX_CHARACTERS = 150
    NORMAL_SENTENCES = 2
    EXTENDED_SENTENCES = 3


SOCCER_MARKERS = re.compile(
    r"サッカー|フットボール|Jリーグ|J[123]|グランパス|日本代表|代表戦|ワールドカップ|"
    r"ACL|ACLE|天皇杯|ルヴァン|リーグ|試合|得点|失点|ゴール|選手|監督|フォーメーション|"
    r"プレス|ビルドアップ|カウンター|守備|攻撃|順位|勝利|敗戦|引き分け"
)

LOSS_PATTERNS = re.compile(r"敗戦|敗れ|負け(?:た|る|試合)?|惨敗|完敗|連敗")
DRAW_PATTERNS = re.compile(r"引き分け|ドロー|勝ち切れず|同点")
WIN_PATTERNS = re.compile(r"勝利|勝った|勝ち試合|快勝|辛勝|連勝")

CURRENT_MARKERS = re.compile(
    r"今日|昨日|現在|現時点|最新|直近|今季|今シーズン|今節|次節|順位|成績|"
    r"スタッツ|移籍|加入|退団|負傷|欠場|監督交代|メンバー|日程|結果|"
    r"20\d{2}(?:年|[-/])|\d{1,2}月\d{1,2}日"
)
