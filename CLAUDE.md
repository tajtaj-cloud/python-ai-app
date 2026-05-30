# CLAUDE.md

このファイルはリポジトリ内のコードを扱う際に Claude Code (claude.ai/code) へ提供するガイダンスです。

## コマンド

```bash
# アプリ起動
streamlit run app.py

# 依存パッケージのインストール
pip install -r requirements.txt
```

## アーキテクチャ

`app.py` 単一ファイルの Streamlit アプリ。サブモジュールなし。

**共通ヘルパー関数（ファイル上部）：**
- `init_gemini()` — `st.session_state["api_key"]` を読み取って `genai` を設定し `GenerativeModel` を返す。キーが未設定の場合は `None` を返しエラーを表示する。
- `generate(model, prompt)` — `model.generate_content()` をスピナーとエラー表示でラップする。
- `show_result(text, filename)` — 生成結果をマークダウンで表示し、ダウンロードボタンを表示する。

**サイドバー（モジュールレベルのコード）：** `.env` の `GEMINI_API_KEY` を起動時のデフォルト値として読み込み、最終的なキーを `st.session_state["api_key"]` に書き込む。ラジオボタンでアクティブなツールを選択する。

**ツールのルーティング（ファイル末尾）：** `tool_map` 辞書がラジオボタンのラベル文字列を各ツール関数にマッピングする。選択中のツール関数は毎回の再実行で無条件に呼び出される（Streamlit はウィジェット操作のたびにスクリプト全体を再実行する）。

**新しいツールを追加する手順：**
1. ウィジェットを描画し、ボタン押下時に `init_gemini()` → `generate()` → `show_result()` を呼ぶ関数（例：`def my_tool():`）を定義する。
2. 同じラベル文字列で `tool_map` にエントリを追加する。
3. サイドバーのラジオボタンの選択肢リストに同じラベル文字列を追加する。

## API キー

起動時に `.env`（`GEMINI_API_KEY=...`）から読み込むか、実行中にサイドバーへ直接入力する。サイドバーの入力が常に優先され、再実行のたびに `st.session_state["api_key"]` を上書きする。形式は `.env.example` を参照。

## モデル

`init_gemini()` 内に `gemini-2.5-flash` がハードコードされている。モデルを変更する場合はその文字列を書き換える。
