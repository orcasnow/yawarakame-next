# やわらかめ対談 CLI

OpenAI Responses APIを使い、記者と忍者／侍がサッカーについて対談する初期実装です。

- 勝利・引き分け: 記者＋忍者
- 敗戦: 記者＋侍
- 既定値: 15往復（30発言）
- Web Search: テーマの時事性をローカル判定して自動実行
- 出力: Markdown＋JSON（各発言後に途中保存）
- キャラクター設定: YAMLを毎回instructionsへ組み込み、RAGは使用しない

## セットアップ

PowerShell:

```powershell
cd C:\Users\lostm\Dropbox\yawarakame-next
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

`OPENAI_API_KEY`は環境変数に設定してください。モデルは`OPENAI_MODEL`で変更できます。

## 実行

```powershell
yawarakame "名古屋グランパスが3-1で勝利した試合を振り返る" --result win
```

テーマを対話入力する場合:

```powershell
yawarakame --result loss
```

主なオプション:

```text
--result auto|win|draw|loss  試合結果。autoで判別不能なら対話入力
--rounds 15                  往復数（1往復は記者＋分析役の2発言）
--search / --no-search       自動判定を明示的に上書き
--model MODEL                使用モデル
--output-dir PATH            出力先
--plan-only                  APIを呼ばず実行計画だけ確認
```

## 自動Web Search判定

「今日」「現在」「今季」「最新」「順位」「移籍」、具体的な日付など、変化しうる情報を含むテーマではWeb Searchを実行します。一般的な戦術論では検索しません。判定結果はJSONとMarkdownに記録されます。

Web Searchは対談の開始時にResearcherが一度実行し、全キャラクターへ同じ調査結果を渡します。キャラクターごとに別々の検索をさせないため、数字や前提の食い違いを抑えられます。

## キャラクター追加

`src/yawarakame/data/characters/`へ同じスキーマのYAMLを追加し、参加者選択ロジックを`director.py`へ追加します。

## テスト

```powershell
pytest
yawarakame "現在の名古屋グランパスの順位を評価する" --result win --plan-only
```
