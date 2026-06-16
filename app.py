import streamlit as st
from gtts import gTTS
import os

# --- 1. ページの設定 ---
st.set_page_config(page_title="タイ語 危機管理単語帳", page_icon="🇹🇭", layout="centered")

# --- 2. データの準備（モックデータ：徐々に難易度が上がるイメージ） ---
# 本来はデータベースやAPIから取得しますが、まずはアプリ内に定義します。
VOCAB_DATA = {
    1: {
        "level_name": "Level 1: 基礎（オフィス・現場の基本）",
        "words": [
            {
                "word": "แจ้ง",
                "pronunciation": "cɛ̂ɛŋ (チェーン)",
                "meaning": "報告する、知らせる、通知する",
                "examples": [
                    {"th": "กรุณาแจ้งให้ทราบทันทีเมื่อมีปัญหา", "jp": "問題が発生した際は、すぐに報告してください。"},
                    {"th": "บริษัทจะแจ้งกำหนดการประชุมให้ทราบอีกครั้ง", "jp": "会社は会議のスケジュールを再度通知します。"}
                ]
            },
            {
                "word": "ปลอดภัย",
                "pronunciation": "plɔ̀ɔt-paj (プロอดパイ)",
                "meaning": "安全な、安全である",
                "examples": [
                    {"th": "ความปลอดภัยในการทำงานต้องมาเป็นอันดับแรก", "jp": "作業における安全が第一でなければなりません。"},
                    {"th": "ตรวจสอบให้แน่ใจว่าพื้นที่นี้ปลอดภัยแล้ว", "jp": "このエリアがすでに安全であることを確認してください。"}
                ]
            }
        ]
    },
    2: {
        "level_name": "Level 2: 中級（トラブル対応・労務）",
        "words": [
            {
                "word": "มาตรการ",
                "pronunciation": "mâat-tra-kaan (マートラカーン)",
                "meaning": "対策、措置、基準",
                "examples": [
                    {"th": "บริษัทกำหนดมาตรการป้องกันข้อมูลรั่วไหลอย่างเข้มงวด", "jp": "会社は、情報漏洩を防止するための厳格な対策を定めています。"},
                    {"th": "โรงงานต้องปฏิบัติตามมาตรการความปลอดภัยอย่างเคร่งครัด", "jp": "工場は安全措置を厳格に遵守しなければなりません。"}
                ]
            },
            {
                "word": "ประท้วง",
                "pronunciation": "pra-thúaŋ (プラトゥアン)",
                "meaning": "抗議する、ストライキをする",
                "examples": [
                    {"th": "พนักงานโรงงานนัดประท้วงเพื่อเรียกร้องสวัสดิการเพิ่ม", "jp": "工場の従業員は、福利厚生の改善を求めてストライキを予定しています。"},
                    {"th": "เราต้องรีบเจรจาก่อนที่การประท้วงจะบานปลาย", "jp": "抗議行動が拡大する前に、私たちは急いで交渉しなければなりません。"}
                ]
            }
        ]
    },
    3: {
        "level_name": "Level 3: 上級（危機管理・BCP専門語彙）",
        "words": [
            {
                "word": "ความต่อเนื่องทางธุรกิจ",
                "pronunciation": "khwaam tɔ̂ɔ-nʉ̂aŋ thaaŋ thú-rá-kìt",
                "meaning": "事業継続（Business Continuity）",
                "examples": [
                    {"th": "การวางแผนความต่อเนื่องทางธุรกิจเป็นสิ่งสำคัญสำหรับองค์กร", "jp": "事業継続計画（BCP）の策定は、組織にとって極めて重要です。"},
                    {"th": "เราต้องรักษาความต่อเนื่องทางธุรกิจแม้ในภาวะวิกฤต", "jp": "私たちは危機下であっても、事業継続を維持しなければなりません。"}
                ]
            },
            {
                "word": "บรรเทาความเสียหาย",
                "pronunciation": "ban-thaw khwaam sǐaj-hǎaj",
                "meaning": "被害を軽減する、緩和する（Mitigation）",
                "examples": [
                    {"th": "มาตรการนี้จะช่วยบรรเทาความเสียหายจากอุทกภัยได้", "jp": "この対策は、洪水による被害を軽減するのに役立ちます。"},
                    {"th": "เราต้องเตรียมพร้อมเพื่อบรรเทาความเสียหายที่อาจจะเกิดขึ้น", "jp": "発生する可能性のある被害を軽減するために、私たちは準備をしておかねばなりません。"}
                ]
            }
        ]
    }
}

# --- 3. アプリのステート管理 ---
# 何日目（どのレベル）を学習しているかを保持します
if "day" not in st.session_state:
    st.session_state.day = 1

current_day = st.session_state.day

# --- 4. 画面の描画 ---
st.title("🇹🇭 タイ語 危機管理単語学習アプリ")
st.subheader(f"Day {current_day} の学習内容")

if current_day in VOCAB_DATA:
    day_data = VOCAB_DATA[current_day]
    st.caption(f"現在の難易度: {day_data['level_name']}")
    st.write("---")

    # 2つの単語をループで表示
    for i, w_info in enumerate(day_data["words"]):
        st.markdown(f"### 単語 {i+1}: <span style='color:#ff4b4b; font-size:32px;'>{w_info['word']}</span>", unsafe_allow_html=True)
        st.write(f"**発音:** {w_info['pronunciation']}")
        st.write(f"**意味:** {w_info['meaning']}")
        
        # 音声生成ボタン
        if st.button(f"🔊 音声を聴く ({w_info['word']})", key=f"audio_{current_day}_{i}"):
            with st.spinner("音声を生成中..."):
                tts = gTTS(text=w_info["word"], lang='th')
                filename = f"speech_{current_day}_{i}.mp3"
                tts.save(filename)
                st.audio(filename, format="audio/mp3")
                # 使用後にファイルを削除したい場合は os.remove(filename) を検討

        st.markdown("#### 📝 例文")
        for ex in w_info["examples"]:
            st.info(f"**泰:** {ex['th']}\n\n**日:** {ex['jp']}")
        
        st.write("---")

    # ナビゲーションボタン
    col1, col2 = st.columns(2)
    with col1:
        if current_day > 1:
            if st.button("⬅️ 前の日の単語へ"):
                st.session_state.day -= 1
                st.rerun()
    with col2:
        if current_day < len(VOCAB_DATA):
            if st.button("次の日の単語へ ➡️"):
                st.session_state.day += 1
                st.rerun()
        else:
            st.success("🎉 現在登録されているすべてのステージをクリアしました！")

else:
    st.error("データが見つかりません。")
