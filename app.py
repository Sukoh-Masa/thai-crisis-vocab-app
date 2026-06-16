import streamlit as st
from gtts import gTTS
import os
import json
from google import genai
from google.genai import types

# --- 1. ページの設定 ---
st.set_page_config(page_title="AIタイ語 危機管理単語帳", page_icon="🇹🇭", layout="centered")

# --- 2. Gemini APIの初期化 ---
# StreamlitのSecretsから安全にAPIキーを読み込みます
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("Gemini APIキーがSecretsに設定されていません。")
    st.stop()

# --- 3. アプリのステート管理 ---
if "day" not in st.session_state:
    st.session_state.day = 1
if "current_words" not in st.session_state:
    st.session_state.current_words = None

# --- 4. AIに単語を生成させる関数 ---
def generate_words_via_ai(day):
    # 難易度の目安を決定
    if day <= 3:
        level_desc = "初級（オフィスや工場の現場で毎日使う基本的な労務・安全・指示の単語）"
    elif day <= 7:
        level_desc = "中級（トラブル対応、抗議行動、規制、役所や警察との連携などで使う実務的な単語）"
    else:
        level_desc = "上級（BCP、事業継続、リスク軽減、地政学リスクなど、危機管理コンサルティングの専門的な語彙）"

    prompt = f"""
    あなたはタイの危機管理コンサルティング会社で働く優秀なAIアシスタントです。
    日本人マーケターが社内や実務で活用するための「タイ語の単語」を2つ厳選し、以下のJSONフォーマットで出力してください。

    【条件】
    - 現在の学習状況: Day {day} （難易度目安: {level_desc}）
    - 各単語に対して、ビジネスや危機管理の現場（特に日系企業の経営層や工場マネージャーとのやり取り）を想定した実用的な例文を「必ず2文ずつ」作成してください。
    - 出力は必ず指定されたJSON形式のみとし、前後の説明テキストは一切含めないでください。

    【出力JSONフォーマット】
    {{
      "words": [
        {{
          "word": "タイ語の単語（例：แจ้ง）",
          "pronunciation": "発音記号やカタカナ読み（例：cɛ̂ɛŋ / チェーン）",
          "meaning": "日本語の意味（例：報告する、通知する）",
          "examples": [
            {{"th": "タイ語の例文1", "jp": "日本語訳1"}},
            {{"th": "タイ語の例文2", "jp": "日本語訳2"}}
          ]
        }},
        ...（合計2単語分）...
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
        # JSONをパースして辞書型として返す
        return json.loads(response.text)
    except Exception as e:
        st.error(f"AIの生成中にエラーが発生しました: {e}")
        return None

# --- 5. 画面の描画 ---
st.title("🇹🇭 AI駆動型：タイ語 危機管理単語帳")
st.write("ボタンを押すと、Geminiが現在のレベルに合わせた実務タイ語を自動生成します。")
st.write("---")

# 初回、または「次の日」に進んだときに、まだその日のデータがなければ生成
if st.session_state.current_words is None:
    with st.spinner(f"Day {st.session_state.day} の単語をAIが生成中..."):
        st.session_state.current_words = generate_words_via_ai(st.session_state.day)

# 生成されたデータの表示
if st.session_state.current_words and "words" in st.session_state.current_words:
    st.subheader(f"📅 Day {st.session_state.day} の学習内容")
    
    # 難易度の簡易表示
    if st.session_state.day <= 3:
        st.caption("現在の難易度: 🟢 初級（現場・オフィスの基本）")
    elif st.session_state.day <= 7:
        st.caption("現在の難易度: 🟡 中級（トラブル対応・労務管理）")
    else:
        st.caption("現在の難易度: 🔴 上級（危機管理・BCP専門語彙）")

    st.write("---")

    for i, w_info in enumerate(st.session_state.current_words["words"]):
        st.markdown(f"### 単語 {i+1}: <span style='color:#ff4b4b; font-size:32px;'>{w_info.get('word', '')}</span>", unsafe_allow_html=True)
        st.write(f"**発音:** {w_info.get('pronunciation', '')}")
        st.write(f"**意味:** {w_info.get('meaning', '')}")
        
        # 音声再生
        word_text = w_info.get('word', '')
        if word_text and st.button(f"🔊 音声を聴く ({word_text})", key=f"audio_{st.session_state.day}_{i}"):
            with st.spinner("音声を生成中..."):
                tts = gTTS(text=word_text, lang='th')
                filename = f"speech_{st.session_state.day}_{i}.mp3"
                tts.save(filename)
                st.audio(filename, format="audio/mp3")

        st.markdown("#### 📝 実務例文")
        for ex in w_info.get("examples", []):
            st.info(f"**泰:** {ex.get('th', '')}\n\n**日:** {ex.get('jp', '')}")
        
        st.write("---")

    # ナビゲーションボタン
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.day > 1:
            if st.button("⬅️ 前の日の単語へ"):
                st.session_state.day -= 1
                st.session_state.current_words = None  # データをクリアして再生成
                st.rerun()
    with col2:
        if st.button("次の日の単語を生成 ➡️"):
            st.session_state.day += 1
            st.session_state.current_words = None  # データをクリアして再生成
            st.rerun()
else:
    st.warning("単語の読み込みに失敗しました。もう一度お試しください。")
    if st.button("再試行"):
        st.rerun()
