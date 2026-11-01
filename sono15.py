import streamlit as st
import sqlite3
from datetime import datetime, date, time, timedelta
import time as t_mod
import random
import pandas as pd

# ==========================================
# データベース設定・初期化
# ==========================================

DB_NAME = "study.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # 予定表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            scheduled_date TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT
        )
    """)

    # タスク
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            range_text TEXT NOT NULL,
            scheduled_date TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)

    # 学習記録
    cur.execute("""
        CREATE TABLE IF NOT EXISTS study_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            minutes INTEGER NOT NULL,
            studied_at TEXT NOT NULL
        )
    """)

    # 単語帳
    cur.execute("""
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            word TEXT NOT NULL,
            meaning TEXT NOT NULL,
            explanation TEXT
        )
    """)

    # クイズ
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            question TEXT NOT NULL,
            choice1 TEXT NOT NULL,
            choice2 TEXT NOT NULL,
            choice3 TEXT NOT NULL,
            choice4 TEXT NOT NULL,
            answer INTEGER NOT NULL,
            explanation TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ==========================================
# DB操作関数
# ==========================================

def add_schedule(title, scheduled_date, start_time, end_time):
    conn = get_connection()
    conn.execute("INSERT INTO schedules (title, scheduled_date, start_time, end_time) VALUES (?, ?, ?, ?)",
                 (title, scheduled_date, start_time, end_time))
    conn.commit()
    conn.close()

def update_schedule(schedule_id, title, scheduled_date, start_time, end_time):
    conn = get_connection()
    conn.execute("UPDATE schedules SET title = ?, scheduled_date = ?, start_time = ?, end_time = ? WHERE id = ?",
                 (title, scheduled_date, start_time, end_time, schedule_id))
    conn.commit()
    conn.close()

def delete_schedule(schedule_id):
    conn = get_connection()
    conn.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
    conn.commit()
    conn.close()

def get_schedules():
    conn = get_connection()
    rows = conn.execute("SELECT id, title, scheduled_date, start_time, end_time FROM schedules ORDER BY scheduled_date").fetchall()
    conn.close()
    return rows

def add_task(subject, range_text, scheduled_date):
    conn = get_connection()
    conn.execute("INSERT INTO tasks (subject, range_text, scheduled_date) VALUES (?, ?, ?)",
                 (subject, range_text, scheduled_date))
    conn.commit()
    conn.close()

def get_today_tasks():
    conn = get_connection()
    today = str(date.today())
    rows = conn.execute("SELECT id, subject, range_text, completed FROM tasks WHERE scheduled_date = ? ORDER BY id", (today,)).fetchall()
    conn.close()
    return rows

def complete_task(task_id):
    conn = get_connection()
    conn.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def add_study_record(subject, minutes):
    conn = get_connection()
    conn.execute("INSERT INTO study_records (subject, minutes, studied_at) VALUES (?, ?, ?)",
                 (subject, minutes, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_total_study_minutes():
    conn = get_connection()
    result = conn.execute("SELECT COALESCE(SUM(minutes), 0) FROM study_records").fetchone()
    conn.close()
    return result[0]

def get_study_records_df():
    conn = get_connection()
    df = pd.read_sql_query("SELECT subject, minutes, studied_at FROM study_records", conn)
    conn.close()
    if not df.empty:
        df["studied_at"] = pd.to_datetime(df["studied_at"])
        df["date"] = df["studied_at"].dt.date
        df["week"] = df["studied_at"].dt.to_period("W").dt.start_time.dt.date
        df["month"] = df["studied_at"].dt.to_period("M").dt.start_time.dt.date
    return df

def add_word(subject, word, meaning, explanation):
    conn = get_connection()
    conn.execute("INSERT INTO words (subject, word, meaning, explanation) VALUES (?, ?, ?, ?)", (subject, word, meaning, explanation))
    conn.commit()
    conn.close()

def update_word(word_id, subject, word, meaning, explanation):
    conn = get_connection()
    conn.execute("UPDATE words SET subject = ?, word = ?, meaning = ?, explanation = ? WHERE id = ?", (subject, word, meaning, explanation, word_id))
    conn.commit()
    conn.close()

def delete_word(word_id):
    conn = get_connection()
    conn.execute("DELETE FROM words WHERE id = ?", (word_id,))
    conn.commit()
    conn.close()

def get_words(subject=None):
    conn = get_connection()
    if subject and subject != "すべて":
        rows = conn.execute("SELECT id, subject, word, meaning, explanation FROM words WHERE subject = ? ORDER BY id DESC", (subject,)).fetchall()
    else:
        rows = conn.execute("SELECT id, subject, word, meaning, explanation FROM words ORDER BY id DESC").fetchall()
    conn.close()
    return rows

def add_quiz(subject, question, choices, answer, explanation):
    conn = get_connection()
    conn.execute("INSERT INTO quizzes (subject, question, choice1, choice2, choice3, choice4, answer, explanation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                 (subject, question, choices[0], choices[1], choices[2], choices[3], answer, explanation))
    conn.commit()
    conn.close()

def update_quiz(quiz_id, subject, question, choices, answer, explanation):
    conn = get_connection()
    conn.execute("""
        UPDATE quizzes 
        SET subject = ?, question = ?, choice1 = ?, choice2 = ?, choice3 = ?, choice4 = ?, answer = ?, explanation = ? 
        WHERE id = ?
    """, (subject, question, choices[0], choices[1], choices[2], choices[3], answer, explanation, quiz_id))
    conn.commit()
    conn.close()

def delete_quiz(quiz_id):
    conn = get_connection()
    conn.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
    conn.commit()
    conn.close()

def get_quizzes(subject=None):
    conn = get_connection()
    if subject and subject != "すべて":
        rows = conn.execute("SELECT id, subject, question, choice1, choice2, choice3, choice4, answer, explanation FROM quizzes WHERE subject = ?", (subject,)).fetchall()
    else:
        rows = conn.execute("SELECT id, subject, question, choice1, choice2, choice3, choice4, answer, explanation FROM quizzes").fetchall()
    conn.close()
    return rows

# ==========================================
# ページ・デザイン・背景・フォント設定
# ==========================================

st.set_page_config(
    page_title="Study Support App",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

today_month = datetime.now().month
if today_month in [3, 4, 5]:
    default_season = "春 (桜)"
elif today_month in [6, 7, 8]:
    default_season = "夏 (青空)"
elif today_month in [9, 10, 11]:
    default_season = "秋 (紅葉)"
else:
    default_season = "冬 (雪)"

st.sidebar.markdown("### 🎨 カスタマイズ設定")
selected_season = st.sidebar.selectbox("背景テーマ", [
    "春 (桜)", "夏 (青空)", "秋 (紅葉)", "冬 (雪)", 
    "宇宙 (夜空)", "パステルミント", "サンセット", "モダン (ダーク)"
], index=["春 (桜)", "夏 (青空)", "秋 (紅葉)", "冬 (雪)", "宇宙 (夜空)", "パステルミント", "サンセット", "モダン (ダーク)"].index(default_season))

font_color_choice = st.sidebar.selectbox("フォントカラー", [
    "ダークネイビー (標準)", "ピュアブラック", "ロイヤルブルー", "ダークグリーン", "ワインレッド", "ホワイト (ダーク背景用)"
])

font_color_map = {
    "ダークネイビー (標準)": "#2c3e50",
    "ピュアブラック": "#000000",
    "ロイヤルブルー": "#1b4f72",
    "ダークグリーン": "#145a32",
    "ワインレッド": "#78281f",
    "ホワイト (ダーク背景用)": "#ffffff"
}
current_font_color = font_color_map[font_color_choice]

selected_weather = st.sidebar.selectbox("天気", ["晴れ", "雨", "くもり"])

bg_styles = {
    "春 (桜)": "linear-gradient(135deg, #fff0f5 0%, #ffe4e1 100%)",
    "夏 (青空)": "linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%)",
    "秋 (紅葉)": "linear-gradient(135deg, #fff8e1 0%, #ffe0b2 100%)",
    "冬 (雪)": "linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%)",
    "宇宙 (夜空)": "linear-gradient(135deg, #141e30 0%, #243b55 100%)",
    "パステルミント": "linear-gradient(135deg, #e8f8f5 0%, #d1f2eb 100%)",
    "サンセット": "linear-gradient(135deg, #ff7e5f 0%, #feb47b 100%)",
    "モダン (ダーク)": "linear-gradient(135deg, #232526 0%, #414345 100%)"
}

card_bg = "rgba(255, 255, 255, 0.9)" if selected_season not in ["宇宙 (夜空)", "モダン (ダーク)"] else "rgba(30, 30, 30, 0.85)"

st.markdown(f"""
<style>
    .stApp {{
        background: {bg_styles[selected_season]};
        color: {current_font_color};
        max-width: 430px;
        margin: 0 auto;
        box-shadow: 0 0 25px rgba(0,0,0,0.12);
        min-height: 100vh;
    }}
    body, p, span, label, h1, h2, h3, h4, h5, h6, .stMarkdown {{
        color: {current_font_color} !important;
    }}
    .main-card {{
        background: {card_bg};
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 16px;
    }}
    
    .touch-box {{
        background: rgba(255, 255, 255, 0.6);
        border: 2px solid rgba(0, 120, 255, 0.15);
        padding: 14px 16px;
        border-radius: 12px;
        margin-bottom: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        transition: all 0.2s ease;
    }}
    .touch-box:hover {{
        border-color: rgba(0, 120, 255, 0.5);
        background: rgba(255, 255, 255, 0.85);
    }}

    .big-timer {{
        font-size: 3.2rem;
        font-weight: bold;
        text-align: center;
        color: #2c3e50;
        background: #ffffff;
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin: 15px 0;
    }}
    .finished-alert {{
        font-size: 2.2rem;
        font-weight: bold;
        text-align: center;
        color: #e74c3c;
        animation: pulse 1s infinite;
    }}
    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.04); }}
        100% {{ transform: scale(1); }}
    }}
    
    button[data-baseweb="tab"] {{
        font-size: 1.15rem !important;
        font-weight: bold !important;
        padding: 12px 20px !important;
    }}

    /* サイドメニューのフォントをさらに大きくし、広めの余白を設定 */
    section[data-testid="stSidebar"] div[data-baseweb="radio"] label div p {{
        font-size: 3.0rem !important;
        font-weight: bold !important;
    }}
    section[data-testid="stSidebar"] div[data-baseweb="radio"] label {{
        padding: 24px 16px !important;
        margin-bottom: 28px !important;
        background-color: rgba(255, 255, 255, 0.15);
        border-radius: 14px;
    }}

    /* 4択クイズの選択肢のフォントをさらに大きくし、広めの余白を設定 */
    div[data-testid="stRadio"] div[data-baseweb="radio"] label div p {{
        font-size: 3.0rem !important;
        font-weight: 600 !important;
    }}
    div[data-testid="stRadio"] div[data-baseweb="radio"] label {{
        padding: 26px 28px !important;
        margin-bottom: 24px !important;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 2px solid rgba(0,0,0,0.06);
        width: 100%;
    }}

    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100% !important;
    }}
</style>
""", unsafe_allow_html=True)

st.title("📚 Study Support")

menu = st.sidebar.radio(
    "メニュー",
    ["ホーム", "予定表", "今日のタスク・タイマー", "学習記録", "単語帳", "4択クイズ", "ランキング"]
)

SUBJECTS = ["数学", "英語", "国語", "理科", "社会", "情報", "その他"]
RANGES = ["教科書・基本問題", "応用・発展問題", "定期テスト対策", "模試・過去問", "暗記・単語確認", "その他"]
TIME_OPTIONS = [10, 15, 25, 30, 45, 60, 90, 120]


# ==========================================
# ホーム
# ==========================================
if menu == "ホーム":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.header("✨ 今日の学習状況")

    tasks = get_today_tasks()
    completed = sum(1 for t in tasks if t[3] == 1)
    total = len(tasks)
    progress = completed / total if total > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("タスク", f"{completed}/{total}")
    with col2:
        st.metric("達成率", f"{progress * 100:.0f}%")
    with col3:
        st.metric("累計時間", f"{get_total_study_minutes()}分")

    st.progress(progress)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📌 今日やること一覧")
    if not tasks:
        st.info("今日のタスクはまだありません。「今日のタスク・タイマー」から追加しましょう！")
    for t in tasks:
        _, sub, rng, is_comp = t
        status_icon = "✓" if is_comp else "□"
        box_color = "rgba(46, 204, 113, 0.15)" if is_comp else "rgba(255, 255, 255, 0.7)"
        st.markdown(f"""
        <div style="background: {box_color}; padding: 12px 15px; border-radius: 10px; margin-bottom: 8px; border: 1px solid rgba(0,0,0,0.08);">
            <b>{status_icon} 【{sub}】</b> {rng}
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 予定表
# ==========================================
elif menu == "予定表":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.header("📅 予定の管理")

    with st.form("schedule_form"):
        st.subheader("新規予定の登録")
        title = st.text_input("予定タイトル")
        scheduled_date = st.date_input("日付", value=date.today())
        col1, col2 = st.columns(2)
        with col1:
            start_time = st.time_input("開始", value=time(9, 0))
        with col2:
            end_time = st.time_input("終了", value=time(10, 0))
        
        submitted = st.form_submit_button("予定を登録")
        if submitted and title:
            add_schedule(title, str(scheduled_date), str(start_time), str(end_time))
            st.toast("📅 予定を登録しました！", icon="🎉")
            t_mod.sleep(0.8)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📋 登録済み予定一覧")
    schedules = get_schedules()
    if not schedules:
        st.info("登録された予定はありません。")

    for sch in schedules:
        s_id, title, d, start, end = sch
        with st.expander(f"📅 {d} {start[:5]}〜{end[:5]} : {title}"):
            with st.form(f"edit_sch_{s_id}"):
                new_title = st.text_input("予定タイトル", value=title, key=f"t_{s_id}")
                new_date = st.date_input("日付", value=datetime.strptime(d, "%Y-%m-%d").date(), key=f"d_{s_id}")
                col_a, col_b = st.columns(2)
                with col_a:
                    new_start = st.time_input("開始", value=datetime.strptime(start, "%H:%M:%S").time() if len(start)>5 else time(9,0), key=f"st_{s_id}")
                with col_b:
                    new_end = st.time_input("終了", value=datetime.strptime(end, "%H:%M:%S").time() if len(end)>5 else time(10,0), key=f"et_{s_id}")
                
                c_col1, c_col2 = st.columns(2)
                with c_col1:
                    if st.form_submit_button("更新"):
                        update_schedule(s_id, new_title, str(new_date), str(new_start), str(new_end))
                        st.toast("✏️ 予定を更新しました！", icon="✨")
                        t_mod.sleep(0.8)
                        st.rerun()
                with c_col2:
                    if st.form_submit_button("削除", type="primary"):
                        delete_schedule(s_id)
                        st.toast("🗑️ 予定を削除しました！", icon="⚠️")
                        t_mod.sleep(0.8)
                        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 今日のタスク ＆ タイマー
# ==========================================
elif menu == "今日のタスク・タイマー":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.header("✅ タスク ＆ タイマー")

    st.subheader("📝 選択式タスクの作成")
    selected_subject = st.selectbox("教科を選択", SUBJECTS)
    selected_range = st.selectbox("達成したい範囲を選択", RANGES)
    
    if st.button("タスクを追加"):
        add_task(selected_subject, selected_range, str(date.today()))
        st.toast("✅ タスクを追加しました！", icon="🎉")
        t_mod.sleep(0.8)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("⏱️ 集中タイマー")

    tasks = get_today_tasks()
    incomplete_tasks = [t for t in tasks if t[3] == 0]

    task_options = [f"{t[1]} - {t[2]}" for t in incomplete_tasks] if incomplete_tasks else ["自由学習"]
    chosen_current_task = st.selectbox("今取り組むタスクを選択", task_options)

    timer_minutes = st.selectbox("時間（分）", TIME_OPTIONS, index=2)

    if "timer_remaining" not in st.session_state:
        st.session_state.timer_remaining = timer_minutes * 60
    if "timer_running" not in st.session_state:
        st.session_state.timer_running = False

    if st.button("タイマーをセット / リセット"):
        st.session_state.timer_remaining = timer_minutes * 60
        st.session_state.timer_running = False
        st.toast("⏱️ タイマーをセットしました！", icon="🔄")
        t_mod.sleep(0.5)
        st.rerun()

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("▶ スタート / 再開"):
            st.session_state.timer_running = True
    with col_btn2:
        if st.button("⏸ 一時停止"):
            st.session_state.timer_running = False

    timer_placeholder = st.empty()
    status_placeholder = st.empty()

    status_placeholder.markdown(f"🔥 **今やるべきこと**: `{chosen_current_task}`")

    minutes_left = st.session_state.timer_remaining // 60
    seconds_left = st.session_state.timer_remaining % 60
    time_str = f"{minutes_left:02d}:{seconds_left:02d}"

    if st.session_state.timer_remaining > 0:
        timer_placeholder.markdown(f'<div class="big-timer">{time_str}</div>', unsafe_allow_html=True)
    else:
        timer_placeholder.markdown(f'<div class="finished-alert">🎉 終了！お疲れ様！ 🎉</div>', unsafe_allow_html=True)

    if st.session_state.timer_running and st.session_state.timer_remaining > 0:
        t_mod.sleep(1)
        st.session_state.timer_remaining -= 1
        st.rerun()
    elif st.session_state.timer_remaining == 0 and st.session_state.timer_running:
        st.session_state.timer_running = False
        add_study_record(chosen_current_task.split(" - ")[0], timer_minutes)
        st.toast("🎉 タイマー終了！学習記録に自動追加しました！", icon="🏆")
        st.balloons()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("✅ タスク一覧（完了チェック）")
    for task in tasks:
        task_id, sub, rng, completed = task
        st.markdown(f"""
        <div class="touch-box">
            <b>【{sub}】</b> {rng}
        </div>
        """, unsafe_allow_html=True)
        if completed:
            st.success("完了済み")
        else:
            if st.button("完了にする", key=f"comp_{task_id}"):
                complete_task(task_id)
                add_study_record(sub, 25)
                st.toast("✨ タスクを完了にし、学習記録に25分追加しました！", icon="🎉")
                t_mod.sleep(0.8)
                st.rerun()
        st.divider()
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 学習記録
# ==========================================
elif menu == "学習記録":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.header("📊 学習記録の管理")

    with st.form("record_form"):
        subject = st.selectbox("教科", SUBJECTS)
        minutes = st.number_input("勉強時間（分）", min_value=1, value=30, step=5)
        if st.form_submit_button("記録を保存"):
            add_study_record(subject, minutes)
            st.toast("📊 学習記録を保存しました！", icon="✨")
            t_mod.sleep(0.8)
            st.rerun()

    st.metric("累計学習時間", f"{get_total_study_minutes()} 分")
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 単語帳（教科別・編集・削除）
# ==========================================
elif menu == "単語帳":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.header("📚 教科別 単語帳")

    with st.form("word_form"):
        st.subheader("新しい単語の登録")
        w_subject = st.selectbox("対象教科", SUBJECTS)
        word = st.text_input("単語・キーワード")
        meaning = st.text_input("意味・訳")
        explanation = st.text_area("解説・例文")
        if st.form_submit_button("単語を登録"):
            if word and meaning:
                add_word(w_subject, word, meaning, explanation)
                st.toast("📚 新しい単語を登録しました！", icon="✨")
                t_mod.sleep(0.8)
                st.rerun()
            else:
                st.error("単語と意味を入力してください。")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📖 登録済み単語一覧")
    filter_subject = st.selectbox("表示する教科を選択", ["すべて"] + SUBJECTS)
    words = get_words(filter_subject)

    if not words:
        st.info("登録されている単語はありません。")

    for w in words:
        w_id, w_sub, word_text, meaning_text, exp_text = w
        with st.expander(f"📖 [{w_sub}] {word_text} : {meaning_text}"):
            with st.form(f"edit_word_{w_id}"):
                nw_sub = st.selectbox("教科", SUBJECTS, index=SUBJECTS.index(w_sub) if w_sub in SUBJECTS else 0, key=f"ws_{w_id}")
                nw = st.text_input("単語", value=word_text, key=f"w_{w_id}")
                nm = st.text_input("意味", value=meaning_text, key=f"m_{w_id}")
                ne = st.text_area("解説", value=exp_text if exp_text else "", key=f"e_{w_id}")
                
                col_w1, col_w2 = st.columns(2)
                with col_w1:
                    if st.form_submit_button("変更を保存"):
                        update_word(w_id, nw_sub, nw, nm, ne)
                        st.toast("✏️ 単語を更新しました！", icon="✨")
                        t_mod.sleep(0.8)
                        st.rerun()
                with col_w2:
                    if st.form_submit_button("削除", type="primary"):
                        delete_word(w_id)
                        st.toast("🗑️ 単語を削除しました！", icon="⚠️")
                        t_mod.sleep(0.8)
                        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 4択クイズ（教科別・挑戦・作成・単語帳自動生成・編集削除）
# ==========================================
elif menu == "4択クイズ":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.header("📝 4択クイズ")

    quiz_tab1, quiz_tab2, quiz_tab3 = st.tabs(["クイズに挑戦", "自分で作成", "単語帳から生成"])

    with quiz_tab1:
        st.subheader("🎯 クイズに挑戦")
        q_filter = st.selectbox("挑戦する教科を選択", ["すべて"] + SUBJECTS, key="q_filter")
        quizzes = get_quizzes(q_filter)

        if not quizzes:
            st.info("この教科のクイズはまだありません。「自分で作成」または「単語帳から生成」でクイズを追加しましょう！")
        else:
            for idx, q in enumerate(quizzes):
                q_id, q_sub, question, c1, c2, c3, c4, answer, explanation = q
                
                with st.expander(f"Q{idx+1} [{q_sub}] {question}"):
                    choices = [c1, c2, c3, c4]
                    selected = st.radio(f"回答を選択 (Q{idx+1})", choices, key=f"quiz_choice_{q_id}")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                    col_ans1, col_ans2 = st.columns(2)
                    with col_ans1:
                        if st.button(f"回答する", key=f"btn_quiz_{q_id}"):
                            if choices.index(selected) == answer:
                                st.success("正解！🎉")
                            else:
                                st.error(f"不正解。正解は「{choices[answer]}」です。")
                            if explanation:
                                st.info(f"解説：{explanation}")
                    
                    st.divider()
                    
                    with st.form(f"edit_quiz_{q_id}"):
                        st.write("✏️ このクイズを編集・削除")
                        eq_sub = st.selectbox("教科", SUBJECTS, index=SUBJECTS.index(q_sub) if q_sub in SUBJECTS else 0, key=f"eq_sub_{q_id}")
                        eq_question = st.text_input("問題文", value=question, key=f"eq_q_{q_id}")
                        eq_c1 = st.text_input("選択肢1 (正解)", value=c1, key=f"eq_c1_{q_id}")
                        eq_c2 = st.text_input("選択肢2", value=c2, key=f"eq_c2_{q_id}")
                        eq_c3 = st.text_input("選択肢3", value=c3, key=f"eq_c3_{q_id}")
                        eq_c4 = st.text_input("選択肢4", value=c4, key=f"eq_c4_{q_id}")
                        eq_ans = st.selectbox("正解の選択肢", [1, 2, 3, 4], index=answer, format_func=lambda x: f"選択肢{x}", key=f"eq_ans_{q_id}")
                        eq_exp = st.text_area("解説", value=explanation if explanation else "", key=f"eq_exp_{q_id}")
                        
                        e_col1, e_col2 = st.columns(2)
                        with e_col1:
                            if st.form_submit_button("更新を保存"):
                                update_quiz(q_id, eq_sub, eq_question, [eq_c1, eq_c2, eq_c3, eq_c4], eq_ans - 1, eq_exp)
                                st.toast("✏️ クイズを更新しました！", icon="✨")
                                t_mod.sleep(0.8)
                                st.rerun()
                        with e_col2:
                            if st.form_submit_button("このクイズを削除", type="primary"):
                                delete_quiz(q_id)
                                st.toast("🗑️ クイズを削除しました！", icon="⚠️")
                                t_mod.sleep(0.8)
                                st.rerun()

    with quiz_tab2:
        st.subheader("✍️ オリジナルクイズの作成")
        with st.form("custom_quiz_form"):
            cq_sub = st.selectbox("教科", SUBJECTS, key="cq_sub")
            cq_question = st.text_input("問題文")
            cq_c1 = st.text_input("選択肢1 (正解にするもの)")
            cq_c2 = st.text_input("選択肢2")
            cq_c3 = st.text_input("選択肢3")
            cq_c4 = st.text_input("選択肢4")
            cq_ans_idx = st.selectbox("正解の選択肢", [1, 2, 3, 4], format_func=lambda x: f"選択肢{x}")
            cq_exp = st.text_area("解説")

            if st.form_submit_button("クイズを追加"):
                if cq_question and cq_c1 and cq_c2 and cq_c3 and cq_c4:
                    choices = [cq_c1, cq_c2, cq_c3, cq_c4]
                    add_quiz(cq_sub, cq_question, choices, cq_ans_idx - 1, cq_exp)
                    st.toast("📝 クイズを追加しました！", icon="🎉")
                    t_mod.sleep(0.8)
                    st.rerun()
                else:
                    st.error("問題文とすべての選択肢を入力してください。")

    with quiz_tab3:
        st.subheader("🔄 単語帳からクイズを自動作成")
        st.write("登録されている単語帳の内容をもとに、自動で4択クイズを生成します。")
        
        gen_sub = st.selectbox("対象の教科を選択", SUBJECTS, key="gen_sub")
        words_in_sub = get_words(gen_sub)

        if len(words_in_sub) < 4:
            st.warning(f"「{gen_sub}」の単語が4つ以上登録されていないと、4択の選択肢が作れません（現在 {len(words_in_sub)} 個）。単語帳から単語を追加してください。")
        else:
            if st.button("単語帳からクイズを生成する"):
                count = 0
                for w in words_in_sub:
                    _, w_sub, word, meaning, exp = w
                    other_meanings = [item[3] for item in words_in_sub if item[3] != meaning]
                    if len(other_meanings) >= 3:
                        dummies = random.sample(other_meanings, 3)
                        choices = dummies + [meaning]
                        random.shuffle(choices)
                        correct_idx = choices.index(meaning)
                        
                        question_text = f"次の言葉の意味は？：【 {word} 】"
                        explanation_text = f"{exp}" if exp else f"{word}の意味は「{meaning}」です。"
                        
                        add_quiz(w_sub, question_text, choices, correct_idx, explanation_text)
                        count += 1
                st.toast(f"🎉 {count}件のクイズを自動生成しました！", icon="✨")
                t_mod.sleep(0.8)
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# ランキング
# ==========================================
elif menu == "ランキング":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.header("🏆 学習ランキング・分析")
    
    total_minutes = get_total_study_minutes()
    st.metric("累計学習時間", f"{total_minutes} 分")
    
    df = get_study_records_df()

    if df.empty:
        st.info("学習記録がまだありません。タイマーや学習記録から勉強時間を記録してみましょう！")
    else:
        # 教科別ランキング
        st.subheader("📖 教科別ランキング")
        sub_df = df.groupby("subject")["minutes"].sum().reset_index()
        sub_df = sub_df.sort_values(by="minutes", ascending=False).reset_index(drop=True)
        sub_df["順位"] = [f"第{i+1}位" for i in range(len(sub_df))]
        sub_df.columns = ["教科", "学習時間 (分)", "順位"]
        st.dataframe(sub_df[["順位", "教科", "学習時間 (分)"]], use_container_width=True, hide_index=True)

        st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)

        # 期間別（日別・週間・月間）の集計とグラフ
        st.subheader("📅 期間別学習時間と推移")
        
        today_date = date.today()
        current_week = pd.Timestamp(today_date).to_period("W").start_time.date()
        current_month = pd.Timestamp(today_date).to_period("M").start_time.date()

        # 日別データ
        daily_df = df.groupby("date")["minutes"].sum().reset_index()
        daily_df["date"] = pd.to_datetime(daily_df["date"])
        daily_df = daily_df.sort_values("date")

        # 週間データ
        weekly_df = df.groupby("week")["minutes"].sum().reset_index()
        weekly_df["week"] = pd.to_datetime(weekly_df["week"])
        weekly_df = weekly_df.sort_values("week")

        # 月間データ
        monthly_df = df.groupby("month")["minutes"].sum().reset_index()
        monthly_df["month"] = pd.to_datetime(monthly_df["month"])
        monthly_df = monthly_df.sort_values("month")

        tab_d, tab_w, tab_m = st.tabs(["日別推移", "週間推移", "月間推移"])

        with tab_d:
            st.write("### ☀️ 日別学習時間")
            if not daily_df.empty:
                today_min = int(daily_df.loc[daily_df["date"].dt.date == today_date, "minutes"].sum()) if today_date in daily_df["date"].dt.date.values else 0
                st.metric("今日の学習時間", f"{today_min} 分")
                
                chart_data = daily_df.set_index("date")["minutes"]
                st.line_chart(chart_data)
            else:
                st.info("データがありません。")

        with tab_w:
            st.write("### 📅 週間学習時間（週単位）")
            if not weekly_df.empty:
                this_week_min = int(weekly_df.loc[weekly_df["week"].dt.date == current_week, "minutes"].sum()) if current_week in weekly_df["week"].dt.date.values else 0
                st.metric("今週の学習時間", f"{this_week_min} 分")
                
                chart_data = weekly_df.set_index("week")["minutes"]
                st.bar_chart(chart_data)
            else:
                st.info("データがありません。")

        with tab_m:
            st.write("### 🗓️ 月間学習時間（月単位）")
            if not monthly_df.empty:
                this_month_min = int(monthly_df.loc[monthly_df["month"].dt.date == current_month, "minutes"].sum()) if current_month in monthly_df["month"].dt.date.values else 0
                st.metric("今月の学習時間", f"{this_month_min} 分")
                
                chart_data = monthly_df.set_index("month")["minutes"]
                st.bar_chart(chart_data)
            else:
                st.info("データがありません。")

    st.markdown('</div>', unsafe_allow_html=True)