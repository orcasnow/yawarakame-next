# yawarakame-next セットアップ手順

この手順では、別のWindows環境へプロジェクトを取得し、仮想環境を作成して、テストとパッケージのビルドができる状態にします。

## 前提

- Windows PowerShell
- Git
- Python 3.13.x
- 有効なOpenAI APIキー（実際に対談を生成するときだけ必要）

Pythonのバージョンを確認します。

```powershell
python --version
git --version
```

Python 3.11以上で動作しますが、現在の開発環境はPython 3.13.9です。環境差を減らすため、可能なら同じメジャー・マイナーバージョンを使用してください。

## GitHubからダウンロードする場合

作業する親フォルダーへ移動して、リポジトリをcloneします。

```powershell
cd C:\Users\<ユーザー名>\Documents
git clone https://github.com/orcasnow/yawarakame-next.git
git checkout main
cd yawarakame-next
```

既にclone済みの場合は、最新のmainを取得します。

```powershell
cd C:\Users\<ユーザー名>\Documents\yawarakame-next
git status
git pull --ff-only origin main
```

`git pull --ff-only`で競合を避けられない場合は、ローカルの変更を確認してから対処してください。共有フォルダーでの同時編集より、環境ごとにcloneし、Gitで変更を共有する運用を推奨します。

## 仮想環境の作成

`.venv`は環境ごとに作成します。別のPCや別のPythonインストールで作成した`.venv`をコピー・共有しないでください。仮想環境には作成時のPythonへの絶対パスが保存されます。

```powershell
cd C:\Users\<ユーザー名>\Documents\yawarakame-next
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

PowerShellの実行ポリシーで有効化が拒否された場合は、現在のユーザーだけに許可してから再実行します。

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
```

プロンプトの先頭に`(.venv)`が表示されれば有効化されています。

## 依存関係のインストール

プロジェクトの依存関係、テストツール、ビルドツールをインストールします。

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
```

`requirements.txt`は現在の開発環境で使用している主要パッケージを固定しています。`pyproject.toml`はパッケージの依存関係とビルド設定の正式な定義です。`pip install -e ".[dev]"`で、ソース変更を反映しながら`yawarakame`コマンドを使用できます。

インストール結果を確認します。

```powershell
python -m pip show openai pydantic PyYAML pytest build
yawarakame --help
```

## APIキーの設定

APIキーはファイルへ保存せず、PowerShellの環境変数として設定します。

現在のPowerShellセッションだけで設定する場合:

```powershell
$env:OPENAI_API_KEY = "<OpenAI APIキー>"
```

Windowsユーザー環境変数として設定する場合:

```powershell
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "<OpenAI APIキー>", "User")
```

後者は新しいPowerShellを開いてから反映を確認してください。モデルを変更する場合は、例えば次のように設定します。

```powershell
$env:OPENAI_MODEL = "gpt-5.6-terra"
```

APIキーの設定確認では、キーそのものを表示しないでください。

```powershell
if ($env:OPENAI_API_KEY) { "OPENAI_API_KEY is set" } else { "OPENAI_API_KEY is not set" }
```

## ビルド前の確認

まずAPIを呼ばない計画表示を実行します。

```powershell
yawarakame "名古屋グランパスが3-1で勝利した試合を振り返る" --result win --rounds 30 --plan-only
```

次にテストを実行します。

```powershell
python -m pytest -q
```

テストが成功しない場合は、ビルド前にエラーを解消してください。特に、`python`と`pip`が`.venv`を指していることを確認します。

```powershell
Get-Command python
Get-Command pip
Get-Command yawarakame
```

いずれもプロジェクトの`.venv\Scripts`配下を指すことが期待されます。

## パッケージのビルド

ビルド前に古い生成物を削除します。`dist`、`build`、`*.egg-info`は生成物なのでGitへ追加しません。

```powershell
Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue
Get-ChildItem -Directory -Filter "*.egg-info" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
python -m build
```

成功すると`dist/`にwheelとsource archiveが生成されます。

```powershell
Get-ChildItem dist
```

wheelの内容を確認する場合:

```powershell
python -m pip install --force-reinstall .\dist\*.whl
```

ただし、開発中は通常、編集可能インストールの`python -m pip install -e ".[dev]"`を使います。

## 実際に対談を生成する

APIキーを設定した状態で実行します。

```powershell
yawarakame "2026年8月26日天皇杯2回戦でガイナーレ鳥取に1-3で逆転負けした試合を振り返る" --result loss --rounds 30
```

結果の指定値は`win`、`draw`、`loss`です。`lose`は使用できません。

生成結果は既定で`output/`へMarkdownとJSONとして保存されます。時事的なテーマではWeb Searchが自動実行されます。

## 別環境での更新手順

```powershell
cd C:\Users\<ユーザー名>\Documents\yawarakame-next
.\.venv\Scripts\Activate.ps1
git pull --ff-only origin main
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
python -m pytest -q
```

Pythonのインストール先を変更した場合や、`.venv`が別環境由来の場合は、既存の`.venv`を使い回さず作り直します。

```powershell
deactivate
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
```

## 共有しないファイル

次のファイルやフォルダーは、環境固有または秘密情報を含むため共有しません。

- `.venv/`
- `.venv-old/`などの仮想環境
- `.env`
- `__pycache__/`
- `.pytest_cache/`
- `output/`
- `smoke_output/`
- `dist/`
- `build/`

これらは`.gitignore`で除外されています。依存関係は`requirements.txt`と`pyproject.toml`、環境変数名は`.env.example`を共有します。
