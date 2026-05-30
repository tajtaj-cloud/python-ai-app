# `app.py` コード解説

## 全体の構造をひと言で言うと

> **「ユーザーの入力をプロンプトに変換して Gemini に投げ、返ってきた文章を画面に表示する」** ——それだけを繰り返すシンプルなアプリです。

---

## 第1層：準備（1〜12行目）

```python
import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
```

最初にライブラリを読み込んでいます。

| ライブラリ | 役割 |
|---|---|
| `streamlit` | 画面（UI）を作るフレームワーク |
| `google.generativeai` | Gemini API を呼び出すライブラリ |
| `os` | 環境変数（APIキー）を読み込む |
| `python-dotenv` | `.env` ファイルを読み込む |

`load_dotenv()` を呼ぶと、`.env` ファイルに書いた `GEMINI_API_KEY=xxx` が自動で環境変数として読み込まれます。

---

## 第2層：3つの共通関数（16〜44行目）

アプリ全体で使い回す「部品」です。どのツールもこの3つを呼ぶだけで完結します。

### `init_gemini()` — AI の起動スイッチ

```python
def init_gemini():
    api_key = st.session_state.get("api_key", "")
    if not api_key:
        st.error("サイドバーに Gemini API キーを入力してください。")
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")
```

- サイドバーに入力された API キーを取り出す
- キーがなければエラーを表示して `None` を返す（処理を止める）
- キーがあれば Gemini モデルを初期化して返す

### `generate()` — AI に文章を作らせる

```python
def generate(model, prompt: str) -> str | None:
    try:
        with st.spinner("生成中..."):
            response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        return None
```

- `st.spinner()` でグルグルのローディング表示を出しながら API を呼ぶ
- `prompt`（指示文）を渡すと AI が生成した文章テキストが返ってくる
- 失敗したらエラーメッセージを表示して `None` を返す

### `show_result()` — 結果を画面に表示する

```python
def show_result(text: str, filename: str):
    st.success("生成完了!")
    st.divider()
    st.markdown(text)
    st.download_button(...)
```

- 緑の「生成完了!」バナーを表示
- 生成されたテキストをマークダウン形式で表示（見出しや箇条書きが綺麗に出る）
- テキストファイルとしてダウンロードできるボタンを追加

---

## 第3層：サイドバー（49〜77行目）

```python
with st.sidebar:
    saved_key = os.getenv("GEMINI_API_KEY", "")  # .envから読む
    api_key = st.text_input("Gemini API Key", value=saved_key, type="password")
    st.session_state["api_key"] = api_key         # 入力値を保存

    tool = st.radio("ツールを選択", [...])         # ツール選択ボタン
```

ポイントが2つあります。

**APIキーの優先順位：**

```
.env ファイル  →  起動時のデフォルト値として表示
サイドバー入力 →  常にこちらが最終的な値として使われる
```

**`st.session_state` とは？**
Streamlit はボタンを押すたびにスクリプト全体を最初から再実行します。その際に値を「記憶」しておく仕組みが `session_state` です。APIキーをここに保存しているので、ページを操作しても消えません。

---

## 第4層：7つのツール関数（82〜402行目）

各ツールはすべて同じパターンで書かれています。

```
1. ウィジェット（入力欄・選択肢）を画面に並べる
2. ボタンが押されたら
   a. 入力チェック → 空なら警告して終了
   b. init_gemini() → AIモデルを取得
   c. プロンプト（指示文）を組み立てる
   d. generate() → AIに生成させる
   e. show_result() → 結果を表示
```

例えばブログ記事執筆はこうなっています。

```python
def blog_writer():
    topic = st.text_input("テーマ・タイトル *")   # ← 入力欄
    tone  = st.selectbox("文体", [...])            # ← 選択肢

    if st.button("記事を生成"):                    # ← ボタン
        model = init_gemini()
        prompt = f"テーマ: {topic}\n文体: {tone}\n..."  # ← 指示文を組み立て
        result = generate(model, prompt)           # ← AIに送る
        show_result(result, "blog.txt")            # ← 表示
```

ユーザーが画面で選んだ内容が、そのままAIへの「指示文（プロンプト）」に埋め込まれる仕組みです。

---

## 第5層：ルーティング（405〜439行目）

```python
tool_map = {
    "📝 ブログ記事執筆": blog_writer,
    "📧 メール返信文生成": email_reply,
    ...
}

tool_map[tool]()  # 選ばれたツールの関数を呼び出す
```

サイドバーで選んだツール名（`tool`）をキーにして辞書を引き、対応する関数を実行します。`if/elif` を並べる代わりに辞書を使うことで、新しいツールを追加するときも `tool_map` に1行足すだけで済みます。

---

## まとめ：データの流れ

```
ユーザーの入力
    ↓
プロンプト（指示文）に組み立て
    ↓
generate() → Gemini API に送信
    ↓
返ってきた文章テキスト
    ↓
show_result() → 画面に表示・ダウンロード
```

コードの9割はこの流れを7種類のツール分だけ繰り返しているだけです。パターンが掴めると、新しいツールを追加するのも簡単にできます。
