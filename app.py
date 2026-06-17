import streamlit as st
from gtts import gTTS
import os
import json
from google import genai
from google.genai import types

# --- 1. ページの設定 ---
st.set_page_config(page_title="AIタイ語 危機管理単語帳", page_icon="🇹🇭", layout="centered")

# --- 2. Gemini APIの初期化 ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("Gemini APIキーがSecretsに設定されていません。")
    st.stop()

# --- 3. アプリのステート管理 ---
if "day" not in st.session_state:
    st.session_state.day = 1

if "word_history" not in st.session_state:
    st.session_state.word_history = {}

# --- 4. AIに単語を生成させる関数 ---
def generate_words_via_ai(day):
    if day <= 3:
        level_desc = "初級（オフィスや工場の現場で毎日使う基本的な労務・安全・指示の単語。一般的な旅行会話は除外）"
    elif day <= 7:
        level_desc = "中級（トラブル対応、抗議行動、ストライキ、規制、役所や警察との連携などで使う実務的な単語）"
    else:
        level_desc = "上級（BCP、事業継続、リスク軽減、地政学リスク、サプライチェーン寸断など、危機管理コンサルティングの専門的な語彙）"

    past_words = []
    for d, data in st.session_state.word_history.items():
        if data and "words" in data:
            for w in data["words"]:
                past_words.append(w.get("word", ""))
    
    exclusion_text = f"ただし、過去に生成した以下の単語は絶対に除外してください：{', '.join(past_words)}" if past_words else ""

    # 【重要】プロンプトをアップデートし、日本語訳の該当箇所に指定タグを埋め込むよう指示
    prompt = f"""
    あなたはタイの危機管理コンサルティング会社で働く優秀なAIアシスタントです。
    日本人マーケターが社内や実務で活用するための「タイ語の単語」を2つ厳選し、以下のJSONフォーマットで出力してください。

    【条件】
    - 現在の学習状況: Day {day} （難易度目安: {level_desc}）
    - {exclusion_text}
    - 各単語に対して、ビジネスや危機管理の現場（特に日系企業の経営層や工場マネージャーとのやり取り）を想定した実用的な例文を「必ず2文ずつ」作成してください。
    - 例文の中には、選定した「タイ語の単語」そのものを必ず正確に含めて作成してください。
    - 日本語訳（jp）の中の、ターゲット単語の意味に該当するキーワード（例：報告する、安全、ストライキなど）の前後を必ず [HL] と [/HL] で囲んでください。
      （例："jp": "問題が発生した際は、すぐに[HL]報告して[/HL]ください。"）
    - 出力は必ず指定されたJSON形式のみとし、前後の説明テキストは一切含めないでください。

    【出力JSONフォーマット】
    {{
      "words": [
        {{
          "word": "タイ語の単語",
          "pronunciation": "発音記号やカタカナ読み",
          "meaning": "日本語の意味",
          "examples": [
            {{"th": "タイ語の例文1", "jp": "日本語訳1（該当ワードを[HL]と[/HL]で囲む）"}},
            {{"th": "タイ語の例文2", "jp": "日本語訳2（該当ワードを[HL]と[/HL]で囲む）"}}
          ]
        }},
        {{
          "word": "別のタイ語の単語",
          "pronunciation": "発音記号やカタカナ読み",
          "meaning": "日本語の意味",
          "examples": [
            {{"th": "タイ語の例文1", "jp": "日本語訳1（該当ワードを[HL]と[/HL]で囲む）"}},
            {{"th": "タイ語の例文2", "jp": "日本語訳2（該当ワードを[HL]と[/HL]で囲む）"}}
          ]
        }}
      ]
    }}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"AIの生成中にエラーが発生しました: {e}")
        return None

# --- 5. データの制御ロジック ---
current_day = st.session_state.day

if current_day not in st.session_state.word_history:
    with st.spinner(f"Day {current_day} の新しい単語をAIが生成中..."):
        generated = generate_words_via_ai(current_day)
        if generated:
            st.session_state.word_history[current_day] = generated

current_words_data = st.session_state.word_history.get(current_day)

# --- 6. 画面の描画 ---
st.title("🇹🇭 AIタイ語 危機管理単語帳")
st.write("---")

if current_words_data and "words" in current_words_data:
    st.subheader(f"📅 Day {current_day} の学習内容")
    
    if current_day <= 3:
        st.caption("現在の難易度: 🟢 初級（現場・オフィスの基本）")
    elif current_day <= 7:
        st.caption("現在の難易度: 🟡 中級（トラブル対応・労務管理）")
    else:
        st.caption("現在の難易度: 🔴 上級（危機管理・BCP専門語彙）")

    st.write("---")

    for i, w_info in enumerate(current_words_data["words"]):
        target_word = w_info.get('word', '').strip()
        
        st.markdown(f"### 単語 {i+1}: <span style='color:#ff4b4b; font-size:28px;'>{target_word}</span>", unsafe_allow_html=True)
        st.write(f"**発音:** {w_info.get('pronunciation', '')}")
        st.write(f"**意味:** {w_info.get('meaning', '')}")
        
        # 音声再生
        if target_word and st.button(f"🔊 音声を聴く ({target_word})", key=f"audio_{current_day}_{i}"):
            with st.spinner("音声を生成中..."):
                tts = gTTS(text=target_word, lang='th')
                filename = f"speech_{current_day}_{i}.mp3"
                tts.save(filename)
                st.audio(filename, format="audio/mp3")

        st.markdown("#### 📝 実務例文")
        for ex_idx, ex in enumerate(w_info.get("examples", [])):
            original_th = ex.get('th', '')
            original_jp = ex.get('jp', '')
            
            # 【タイ語】ターゲット単語を濃い赤（#C00000）の太字に変形
            if target_word and target_word in original_th:
                highlighted_th = original_th.replace(
                    target_word, 
                    f"<span style='color:#C00000; font-weight:bold; font-size:22px;'>{target_word}</span>"
                )
            else:
                highlighted_th = original_th

            # 【日本語】AIが付けてくれた [HL] タグを、同じ濃い赤（#C00000）の太字に置換
            highlighted_jp = original_jp.replace(
                "[HL]", f"<span style='color:#C00000; font-weight:bold; font-size:17px;'>"
            ).replace(
                "[/HL]", "</span>"
            )

            # HTML表示用のコンテナボックス
            st.markdown(
                f"""
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 12px; border-left: 5px solid #ff4b4b; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <p style="margin: 0 0 8px 0; color: #111111; font-size: 18px; line-height: 1.7;"><strong>泰:</strong> {highlighted_th}</p>
                    <p style="margin: 0; color: #444444; font-size: 15px; line-height: 1.5;"><strong>日:</strong> {highlighted_jp}</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        st.write("---")

    # ナビゲーションボタン
    col1, col2 = st.columns(2)
    with col1:
        if current_day > 1:
            if st.button("⬅️ 前の日の単語へ"):
                st.session_state.day -= 1
                st.initial_rerun() if hasattr(st, "initial_rerun") else st.rerun()
    with col2:
        if st.button("次の日の単語を生成 ➡️"):
            st.session_state.day += 1
            st.initial_rerun() if hasattr(st, "initial_rerun") else st.rerun()
else:
    st.warning("単語の読み込みに失敗しました。ボタンを押して再試行してください。")
    if st.button("再試行"):
        st.initial_rerun() if hasattr(st, "initial_rerun") else st.rerun()
