# やわらかめ対談 CLI

OpenAI Responses APIを使って、記者と分析役がサッカーの試合や戦術を対談形式で振り返るCLIアプリです。
キャラクター設定はYAMLで管理し、検索結果や過去ログをキャラクター選択に使うRAGは採用していません。

## 現在の仕様

- 勝利・引き分け: 記者＋忍者
- 敗戦: 記者＋侍
- 対応分野: サッカーのみ
- 往復数: 既定30、1〜30の範囲で指定可能（発言数は往復数の2倍）
- モデル: 既定`gpt-5.6-terra`、`OPENAI_MODEL`または`--model`で変更可能
- Web Search: テーマに時事性があるかをローカル判定し、必要な場合だけ対談開始時に一度実行
- 出力: MarkdownとJSON
- 保存: 調査後および各発言後に状態を保存。APIエラーや中断時も途中結果を残す
- 発話制限: すべての発言は150文字以内。通常は2文以内、まとめと締めは3文以内

## 対談の進行

記者と分析役は、常に記者から始まり、交互に発言します。最初の6往復は導入です。

1. 自己紹介: 記者が対談を始め、分析役が結果を踏まえた第一印象を述べる
2. 結果の整理: スコアや勝敗を共有し、試合全体の大きな流れを確認する
3. 結果に関するボケ・雑談（1）
4. 結果に関するボケ・雑談（2）
5. 結果に関するボケ・雑談（3）
6. スターティングメンバーの確認と評論: 記者がスタメン構成について尋ね、分析役が狙いや気になる点を評論する
7. 掘り下げ: 根拠、反例、ファン目線、相手の狙いなどを扱う
8. 試合の評価: closingの前に、良かった点と改善点を箇条書きで整理する
9. 最後に: 最後の5往復で議論をまとめ、固定の締め文で終了する

導入も1往復として数えられます。評価とclosingを含めるには、少なくとも5往復を指定してください。標準の30往復では最後の5往復がclosingです。

評価セクションの見出しは`## この試合の良かったところ`と`## この試合の(´ε｀；)ｳｰﾝ…`です。各セクションには対談内容から最大3件の箇条書きを生成します。その後、`## 最後に`としてclosingを出力します。

closingの最後の3発言はアプリケーション側で固定しています。忍者の場合は「おあとがよろしいようで」→「それではまた次の記事でお会いいたしましょう」→「ﾆﾝﾆﾝ」、侍の場合は「お後がよろしいようで」→「それではまた次の記事でお会いいたしましょう」→「成敗！（Say-Bye！)」です。

## セットアップ

別環境への取得からビルドまでの詳細な手順は [SETUP.md](SETUP.md) を参照してください。

PowerShell:

```powershell
cd C:\Users\lostm\Dropbox\yawarakame-next
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

`OPENAI_API_KEY`を環境変数に設定してください。モデルは`OPENAI_MODEL`で変更できます。任意で`OPENAI_SAFETY_IDENTIFIER`を設定できます。秘密情報をYAMLやソースコードへ直接記載しないでください。

## 実行

```powershell
yawarakame "名古屋グランパスが3-1で勝利した試合を振り返る" --result win
yawarakame "名古屋グランパスが3-1で勝利した試合を振り返る" --result win --rounds 15
```

テーマを対話入力する場合:

```powershell
yawarakame --result loss
```

主なオプション:

```text
--result auto|win|draw|loss  試合結果。既定はauto
--rounds N                  往復数。既定30、1〜30、発言数は2倍
--search / --no-search      Web Searchの自動判定を上書き
--model MODEL               使用するOpenAIモデル
--output-dir PATH           Markdown/JSONの出力先。既定はoutput
--plan-only                 APIを呼ばず実行計画だけ表示
```

`auto`ではテーマから結果を推定します。`勝利`、`勝った`、`快勝`、`辛勝`などは`win`、`引き分け`、`ドロー`などは`draw`、`敗戦`、`負け`、`逆転負け`、`惨敗`などは`loss`です。判別できない場合、対話可能な端末では入力を促し、非対話環境ではエラーになります。

`--plan-only`はAPIを呼ばず、テーマ、結果、参加者、往復数、Web Searchの状態、モデルを表示します。

## 自動Web Search判定

`今日`、`現在`、`最新`、`今季`、`今節`、`順位`、`成績`、`スタッツ`、`移籍`、`加入`、`退団`、`負傷`、`欠場`、`監督交代`、`メンバー`、`日程`、`結果`、具体的な年や日付などを含むテーマではWeb Searchを実行します。一般的な戦術論では検索しません。

Web Searchは対談開始時にResearcherが一度実行します。最大3回の検索ツール呼び出しを許可し、同じ調査結果を記者と分析役の両方へ渡します。`--search`と`--no-search`で自動判定を上書きできます。

検索結果のURLはMarkdownの「参考情報」とJSONの`research.sources`に保存されます。発言中にはURLや出典一覧を表示しません。

## 出力ファイル

既定では`output/`へ次の2ファイルを保存します。

```text
output/
  YYYYMMDD-HHMMSS-テーマのスラッグ-セッションID先頭8文字.md
  YYYYMMDD-HHMMSS-テーマのスラッグ-セッションID先頭8文字.json
```

Markdownにはテーマ、結果区分、往復数、モデル、状態、検索判定、対談、参考情報が含まれます。JSONには各発言の話者、フェーズ、発言目的、本文、時刻、調査情報、セッション状態が含まれます。

`--output-dir`または`YAWARAKAME_OUTPUT_DIR`で保存先を変更できます。生成中も同じファイルを保存するため、中断時は途中結果を確認できます。現時点では途中状態からの自動再開コマンドはありません。

## キャラクター

定義は`src/yawarakame/data/characters/`にあります。

- `reporter.yaml`: 対談の進行、論点整理、ファン目線を担当する記者
- `ninja.yaml`: 勝利・引き分け時の戦術分析を担当する忍者
- `samurai.yaml`: 敗戦時の敗因分析と改善点の検証を担当する侍

各YAMLは`id`、`name`、`label`、`role`、`worldview`、`voice`、`relationships`、`examples`のスキーマです。設定は発言ごとにOpenAIの`instructions`へ組み込まれます。新しいYAMLは自動的に読み込まれますが、参加者選択は現在試合結果に固定されているため、新キャラクターを参加させるには`src/yawarakame/director.py`の`participant_ids()`などを変更してください。

## 構成

```text
src/yawarakame/
  constants.py       数値、正規表現、環境変数の既定値、API制限
  cli.py            CLI引数、サッカー判定、結果・検索設定
  director.py       参加者選択と各発言のフェーズ・目的
  research.py       Web Search判定、調査、出典抽出
  actor.py          キャラクター発話の生成とローリング要約
  engine.py         調査・発話・保存の実行制御
  characters.py     YAMLキャラクターの読み込み
  models.py         Pydanticによる状態・発言・設定モデル
  output.py         Markdown・JSON出力
  data/characters/  記者、忍者、侍のYAML定義
tests/                ユニットテスト
```

## テスト

```powershell
pytest
yawarakame "現在の名古屋グランパスの順位を評価する" --result win --plan-only
```

テストでは、結果判定、参加者選択、openingからclosingまでの発言計画、発話の長さ制限、Markdown・JSON出力、Web Search判定を確認します。

## 注意事項

- OpenAI APIの利用には、有効なAPIキーと利用可能なモデルが必要です。
- 生成されたスコア、順位、選手情報などは公開前に事実確認してください。
- 対談は最大30往復で、長い対談では6発言ごとにローリング要約を作成します。
- APIエラーの詳細は認証情報を除去して状態へ保存します。
- 現在はサッカー以外のテーマを受け付けません。
