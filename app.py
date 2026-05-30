import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI ライティングツール",
    page_icon="✍️",
    layout="wide",
)

# ---------- Gemini helpers ----------

def init_gemini():
    api_key = st.session_state.get("api_key", "")
    if not api_key:
        st.error("サイドバーに Gemini API キーを入力してください。")
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")


def generate(model, prompt: str) -> str | None:
    try:
        with st.spinner("生成中..."):
            response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        return None


def show_result(text: str, filename: str):
    st.success("生成完了!")
    st.divider()
    st.markdown(text)
    st.download_button(
        label="テキストをダウンロード",
        data=text,
        file_name=filename,
        mime="text/plain",
    )


# ---------- Sidebar ----------

with st.sidebar:
    st.title("✍️ AI ライティングツール")

    saved_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input(
        "Gemini API Key",
        value=saved_key,
        type="password",
        help="Google AI Studio で取得したキーを入力してください",
    )
    st.session_state["api_key"] = api_key

    st.divider()

    tool = st.radio(
        "ツールを選択",
        [
            "📝 ブログ記事執筆",
            "📧 メール返信文生成",
            "📋 文章要約",
            "✏️ 文章校正・改善",
            "📱 SNS投稿文生成",
            "🎯 タイトル・見出し生成",
            "🔄 文章言い換え",
        ],
    )

    st.divider()
    st.caption("Powered by Gemini API")


# ---------- Tool: Blog Writer ----------

def blog_writer():
    st.header("📝 ブログ記事執筆")
    st.caption("テーマや条件を入力するとブログ記事を執筆します。")

    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("テーマ・タイトル *", placeholder="例：Pythonでできること10選")
        target = st.text_input("ターゲット読者", placeholder="例：プログラミング初心者")
        tone = st.selectbox("文体", ["です・ます調（丁寧）", "だ・である調（硬い）", "カジュアル"])
    with col2:
        keywords = st.text_area("キーワード（任意）", placeholder="例：Python, 機械学習, 初心者", height=100)
        length = st.select_slider("目標文字数", ["500字", "800字", "1000字", "1500字", "2000字以上"])

    sections = st.multiselect(
        "含める要素",
        ["導入文", "見出し構成", "本文", "まとめ", "CTA（行動喚起）"],
        default=["導入文", "見出し構成", "本文", "まとめ"],
    )
    additional = st.text_area("追加指示（任意）", placeholder="例：具体的な例を多く含めてください")

    if st.button("記事を生成", type="primary", use_container_width=True):
        if not topic:
            st.warning("テーマを入力してください。")
            return
        model = init_gemini()
        if not model:
            return
        prompt = f"""あなたはSEOに精通したプロのブログライターです。
以下の条件で、検索上位を狙えるSEO最適化されたブログ記事を執筆してください。

【基本条件】
テーマ: {topic}
ターゲット読者: {target or '一般読者'}
文体: {tone}
目標文字数: {length}
{f'メインキーワード: {keywords}' if keywords else ''}
含める要素: {', '.join(sections)}
{f'追加指示: {additional}' if additional else ''}

【SEO要件】
- タイトルにメインキーワードを含め、クリックされやすい魅力的な表現にする
- 導入文の冒頭100字以内にメインキーワードを自然に含める
- H2・H3見出しにキーワードや関連語を適切に盛り込む
- 検索意図（知りたい・やりたい・行きたい・買いたい）を満たす構成にする
- 同義語・関連語を本文中に自然に散りばめる（LSIキーワード）
- 読者の疑問に先回りして答えるFAQ的な視点を含める
- 具体的な数字・事例・根拠を入れて信頼性（E-E-A-T）を高める
- 最後に読者が次に取るべき行動（CTA）を明示する

日本語で出力してください。"""
        result = generate(model, prompt)
        if result:
            show_result(result, f"blog_{topic[:20].replace(' ', '_')}.txt")


# ---------- Tool: Email Reply ----------

def email_reply():
    st.header("📧 メール返信文生成")
    st.caption("受信メールと返信の意図を入力すると返信文を生成します。")

    original = st.text_area("受信メール *", placeholder="受信したメールの内容を貼り付けてください", height=200)

    col1, col2 = st.columns(2)
    with col1:
        intent = st.text_area("返信の意図・ポイント *", placeholder="例：承諾する、来週火曜日が都合よい", height=100)
        tone = st.selectbox("文体・雰囲気", ["丁寧・フォーマル", "ビジネスカジュアル", "友好的・カジュアル"])
    with col2:
        sender_role = st.text_input("送信者の立場（任意）", placeholder="例：上司、取引先")
        your_role = st.text_input("あなたの立場（任意）", placeholder="例：部下、担当者")

    if st.button("返信文を生成", type="primary", use_container_width=True):
        if not original or not intent:
            st.warning("受信メールと返信の意図を入力してください。")
            return
        model = init_gemini()
        if not model:
            return
        prompt = f"""以下のメールへの返信文を生成してください。

【受信メール】
{original}

【返信の意図・ポイント】
{intent}

文体: {tone}
{f'送信者の立場: {sender_role}' if sender_role else ''}
{f'あなたの立場: {your_role}' if your_role else ''}

件名と本文を含む自然な日本語のビジネスメールとして生成してください。"""
        result = generate(model, prompt)
        if result:
            show_result(result, "email_reply.txt")


# ---------- Tool: Summarizer ----------

def text_summarizer():
    st.header("📋 文章要約")
    st.caption("長い文章を要点をまとめて短く要約します。")

    text = st.text_area("要約する文章 *", placeholder="要約したい文章を貼り付けてください", height=300)

    col1, col2 = st.columns(2)
    with col1:
        length = st.select_slider(
            "要約の長さ", ["3行以内", "5行以内", "100字以内", "200字以内", "300字以内", "箇条書き5点"]
        )
    with col2:
        style = st.selectbox(
            "要約スタイル", ["ポイントを絞った要約", "箇条書き形式", "一言要約＋詳細", "Q&A形式"]
        )

    focus = st.text_input("重点的にまとめたい観点（任意）", placeholder="例：結論、数値データ、問題点と解決策")

    if st.button("要約する", type="primary", use_container_width=True):
        if not text:
            st.warning("要約する文章を入力してください。")
            return
        model = init_gemini()
        if not model:
            return
        prompt = f"""以下の文章を要約してください。

【文章】
{text}

要約の長さ: {length}
スタイル: {style}
{f'重点観点: {focus}' if focus else ''}

日本語で読みやすく的確な要約を作成してください。"""
        result = generate(model, prompt)
        if result:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("元の文字数", f"{len(text):,} 字")
            with col2:
                st.metric("要約後の文字数", f"{len(result):,} 字")
            show_result(result, "summary.txt")


# ---------- Tool: Proofreader ----------

def text_proofreader():
    st.header("✏️ 文章校正・改善")
    st.caption("文章の誤字脱字を修正し、読みやすく改善します。")

    text = st.text_area("校正・改善する文章 *", placeholder="校正したい文章を貼り付けてください", height=250)

    items = st.multiselect(
        "改善する項目",
        ["誤字脱字の修正", "読みやすさの改善", "文法・表現の修正", "語彙の豊富化", "論理構成の整理", "敬語・丁寧語の統一"],
        default=["誤字脱字の修正", "読みやすさの改善", "文法・表現の修正"],
    )

    col1, col2 = st.columns(2)
    with col1:
        target_tone = st.selectbox(
            "目標とする文体",
            ["原文に近い文体を維持", "です・ます調に統一", "だ・である調に統一", "よりフォーマルに", "よりカジュアルに"],
        )
    with col2:
        show_diff = st.checkbox("修正箇所の説明を表示", value=True)

    if st.button("校正・改善する", type="primary", use_container_width=True):
        if not text:
            st.warning("校正する文章を入力してください。")
            return
        model = init_gemini()
        if not model:
            return
        diff_instruction = "最後に修正箇所と理由を箇条書きで示してください。" if show_diff else ""
        prompt = f"""以下の文章を校正・改善してください。

【文章】
{text}

改善項目: {', '.join(items)}
目標文体: {target_tone}

改善後の文章を最初に示し、{diff_instruction}
日本語で処理してください。"""
        result = generate(model, prompt)
        if result:
            show_result(result, "proofread.txt")


# ---------- Tool: SNS Post Generator ----------

def sns_post_generator():
    st.header("📱 SNS投稿文生成")
    st.caption("テーマから各SNS向けの投稿文を生成します。")

    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_area(
            "投稿したい内容・テーマ *", placeholder="例：新しいブログ記事を公開した、新サービスのお知らせ", height=120
        )
        platforms = st.multiselect(
            "SNSプラットフォーム",
            ["X (Twitter)", "Instagram", "Facebook", "LinkedIn", "Threads"],
            default=["X (Twitter)"],
        )
    with col2:
        tone = st.selectbox("トーン", ["プロフェッショナル", "フレンドリー", "ユーモラス", "インスピレーション", "情報提供"])
        include_hashtags = st.checkbox("ハッシュタグを含める", value=True)
        include_emoji = st.checkbox("絵文字を含める", value=True)

    url = st.text_input("URL（任意）", placeholder="例：https://example.com/blog/post")

    if st.button("投稿文を生成", type="primary", use_container_width=True):
        if not topic:
            st.warning("投稿したい内容を入力してください。")
            return
        if not platforms:
            st.warning("プラットフォームを選択してください。")
            return
        model = init_gemini()
        if not model:
            return
        prompt = f"""以下の内容で各SNS向けの投稿文を生成してください。

【内容・テーマ】
{topic}

プラットフォーム: {', '.join(platforms)}
トーン: {tone}
{'ハッシュタグ: 適切なハッシュタグを含めてください。' if include_hashtags else ''}
{'絵文字: 適切な絵文字を含めてください。' if include_emoji else ''}
{f'URL: {url}' if url else ''}

各プラットフォームの文字数制限と特性に合わせ、プラットフォーム別に日本語で生成してください。"""
        result = generate(model, prompt)
        if result:
            show_result(result, "sns_posts.txt")


# ---------- Tool: Title Generator ----------

def title_generator():
    st.header("🎯 タイトル・見出し生成")
    st.caption("コンテンツの内容からキャッチーなタイトルや見出しを生成します。")

    content = st.text_area("コンテンツの概要・内容 *", placeholder="記事や動画の概要を入力してください", height=150)

    col1, col2 = st.columns(2)
    with col1:
        content_type = st.selectbox(
            "コンテンツタイプ", ["ブログ記事", "ニュース記事", "YouTube動画", "プレゼン", "メルマガ", "LP・広告"]
        )
        count = st.slider("生成する数", 3, 10, 5)
    with col2:
        styles = st.multiselect(
            "タイトルスタイル",
            ["数字を使う", "疑問形", "How-to形式", "ベネフィット強調", "緊急性・限定感", "感情を刺激"],
            default=["数字を使う", "疑問形", "ベネフィット強調"],
        )
        keywords = st.text_input("含めたいキーワード（任意）", placeholder="例：Python, 初心者")

    if st.button("タイトルを生成", type="primary", use_container_width=True):
        if not content:
            st.warning("コンテンツの概要を入力してください。")
            return
        model = init_gemini()
        if not model:
            return
        prompt = f"""以下のコンテンツ用のタイトルを{count}個生成してください。

【コンテンツ概要】
{content}

コンテンツタイプ: {content_type}
スタイル指定: {', '.join(styles) if styles else '特になし'}
{f'含めるキーワード: {keywords}' if keywords else ''}

SEOと読者の興味を引く観点から多様なアプローチで{count}個のタイトル案を生成し、
それぞれに特徴を一言添えてください。日本語で生成してください。"""
        result = generate(model, prompt)
        if result:
            show_result(result, "titles.txt")


# ---------- Tool: Paraphraser ----------

def text_paraphraser():
    st.header("🔄 文章言い換え")
    st.caption("同じ内容を別の表現や文体で言い換えます。")

    text = st.text_area("言い換える文章 *", placeholder="言い換えたい文章を入力してください", height=200)

    col1, col2 = st.columns(2)
    with col1:
        target_style = st.selectbox(
            "目標スタイル",
            [
                "よりフォーマルに",
                "よりカジュアルに",
                "よりシンプルに",
                "より詳しく・豊かに",
                "よりポジティブな表現に",
                "より説得力のある表現に",
            ],
        )
        count = st.slider("バリエーション数", 1, 5, 3)
    with col2:
        keep_meaning = st.checkbox("意味を完全に保持する", value=True)
        audience = st.selectbox(
            "想定読者", ["一般読者", "専門家向け", "子供・学生向け", "ビジネスパーソン向け"]
        )

    if st.button("言い換える", type="primary", use_container_width=True):
        if not text:
            st.warning("言い換える文章を入力してください。")
            return
        model = init_gemini()
        if not model:
            return
        meaning_note = "元の意味を完全に保持してください。" if keep_meaning else "意味を概ね保持しつつ、表現を自由に変えてください。"
        prompt = f"""以下の文章を{count}つのバリエーションで言い換えてください。

【元の文章】
{text}

目標スタイル: {target_style}
想定読者: {audience}
制約: {meaning_note}

各バリエーションに番号を付けてスタイルの特徴を一言添えてください。日本語で生成してください。"""
        result = generate(model, prompt)
        if result:
            show_result(result, "paraphrase.txt")


# ---------- Routing ----------

if not st.session_state.get("api_key"):
    st.info("👈 サイドバーに Gemini API キーを入力してください。")
    st.markdown("""
### はじめに

1. [Google AI Studio](https://aistudio.google.com/app/apikey) で API キーを取得
2. 左サイドバーに API キーを入力
3. 使いたいツールをサイドバーから選択

### 機能一覧

| ツール | 説明 |
|--------|------|
| 📝 ブログ記事執筆 | テーマや条件からブログ記事を自動生成 |
| 📧 メール返信文生成 | 受信メールへの返信文を作成 |
| 📋 文章要約 | 長文を手軽に要約 |
| ✏️ 文章校正・改善 | 誤字・表現を修正して読みやすく |
| 📱 SNS投稿文生成 | 各SNSに最適化した投稿文を作成 |
| 🎯 タイトル・見出し生成 | キャッチーなタイトル案を複数提案 |
| 🔄 文章言い換え | 同内容を別表現・別文体に変換 |
""")

tool_map = {
    "📝 ブログ記事執筆": blog_writer,
    "📧 メール返信文生成": email_reply,
    "📋 文章要約": text_summarizer,
    "✏️ 文章校正・改善": text_proofreader,
    "📱 SNS投稿文生成": sns_post_generator,
    "🎯 タイトル・見出し生成": title_generator,
    "🔄 文章言い換え": text_paraphraser,
}

tool_map[tool]()
