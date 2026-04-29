import csv
import io
import sqlite3
from datetime import date, datetime, timedelta

import streamlit as st


DB_PATH = "thai_study.db"
DEFAULT_MODEL = "gpt-5.2"
TRANSCRIBE_MODEL = "gpt-4o-mini-transcribe"

SAMPLE_WORDS = [
    ("สวัสดี", "sawatdee", "hello / goodbye", "greetings", "Polite everyday greeting."),
    ("ขอบคุณ", "khop khun", "thank you", "manners", "Add ค่ะ/ครับ for politeness."),
    ("ใช่", "chai", "yes / correct", "basics", "Affirming something is correct."),
    ("ไม่ใช่", "mai chai", "no / not correct", "basics", "Denying a statement."),
    ("น้ำ", "nam", "water", "food", "Also appears in many compound words."),
    ("กาแฟ", "gaa-fae", "coffee", "food", "Useful for cafe practice."),
    ("เท่าไหร่", "tao rai", "how much", "shopping", "Question word for price or amount."),
    ("ห้องน้ำ", "hong nam", "bathroom", "travel", "Literally water room."),
    ("อร่อย", "a-roi", "delicious", "food", "Good praise after eating."),
    ("ช้าๆ", "chaa chaa", "slowly", "conversation", "Useful phrase: พูดช้าๆได้ไหม"),
]

LESSONS = [
    ("Greetings", "สวัสดีค่ะ", "Hello.", "Practice polite particles ค่ะ and ครับ."),
    ("Introductions", "ฉันชื่อ...", "My name is...", "Say your name and ask คุณชื่ออะไร."),
    ("Numbers", "หนึ่ง สอง สาม", "One, two, three.", "Count prices and quantities."),
    ("Telling time", "กี่โมงแล้ว", "What time is it?", "Use โมง and นาที."),
    ("Days", "วันนี้วันอะไร", "What day is today?", "Use วันนี้, พรุ่งนี้, เมื่อวาน."),
    ("Colors", "เสื้อสีแดง", "A red shirt.", "Use สี before color words."),
    ("Household items", "โต๊ะอยู่ในบ้าน", "The table is in the house.", "Name things around your home."),
    ("Food and drink", "ขอน้ำหนึ่งแก้ว", "One glass of water, please.", "Order simple food and drinks."),
    ("Shopping", "ราคาเท่าไหร่", "How much is it?", "Ask prices and answer with บาท."),
    ("Directions", "ตรงไปแล้วเลี้ยวซ้าย", "Go straight, then turn left.", "Practice ซ้าย and ขวา."),
]


def connect():
    return sqlite3.connect(DB_PATH)


def init_db():
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thai TEXT NOT NULL,
                romanization TEXT,
                english TEXT NOT NULL,
                category TEXT,
                notes TEXT,
                ease REAL DEFAULT 2.5,
                interval_days INTEGER DEFAULT 0,
                repetitions INTEGER DEFAULT 0,
                due_on TEXT DEFAULT CURRENT_DATE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(thai, english)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER NOT NULL,
                grade TEXT NOT NULL,
                reviewed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(card_id) REFERENCES cards(id)
            )
            """
        )


def add_card(thai, romanization, english, category="", notes=""):
    with connect() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO cards (thai, romanization, english, category, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (thai.strip(), romanization.strip(), english.strip(), category.strip(), notes.strip()),
        )


def load_cards(only_due=False):
    query = "SELECT id, thai, romanization, english, category, notes, ease, interval_days, repetitions, due_on FROM cards"
    params = []
    if only_due:
        query += " WHERE due_on <= ?"
        params.append(date.today().isoformat())
    query += " ORDER BY due_on ASC, id DESC"
    with connect() as conn:
        return conn.execute(query, params).fetchall()


def review_card(card, grade):
    card_id, _, _, _, _, _, ease, interval_days, repetitions, _ = card
    if grade == "again":
        repetitions = 0
        interval_days = 1
        ease = max(1.3, ease - 0.25)
    elif grade == "good":
        repetitions += 1
        interval_days = 1 if repetitions == 1 else max(2, round(interval_days * ease))
    else:
        repetitions += 1
        ease += 0.15
        interval_days = 3 if repetitions == 1 else max(4, round(interval_days * ease * 1.35))

    due_on = (date.today() + timedelta(days=interval_days)).isoformat()
    with connect() as conn:
        conn.execute(
            """
            UPDATE cards
            SET ease = ?, interval_days = ?, repetitions = ?, due_on = ?
            WHERE id = ?
            """,
            (ease, interval_days, repetitions, due_on, card_id),
        )
        conn.execute("INSERT INTO reviews (card_id, grade) VALUES (?, ?)", (card_id, grade))


def parse_vocab_upload(file):
    text = file.getvalue().decode("utf-8-sig")
    dialect = csv.excel_tab if "\t" in text.splitlines()[0] else csv.excel
    rows = list(csv.reader(io.StringIO(text), dialect=dialect))
    if rows and rows[0] and rows[0][0].lower() in {"thai", "word", "คำ"}:
        rows = rows[1:]
    for row in rows:
        if len(row) >= 2 and row[0].strip():
            thai = row[0]
            romanization = row[1] if len(row) > 1 else ""
            english = row[2] if len(row) > 2 else row[1]
            category = row[3] if len(row) > 3 else "uploaded"
            notes = row[4] if len(row) > 4 else ""
            add_card(thai, romanization, english, category, notes)


def get_api_key():
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
    return st.session_state.get("api_key", "")


def has_secret_api_key():
    try:
        return "OPENAI_API_KEY" in st.secrets
    except Exception:
        return False


def openai_client():
    from openai import OpenAI

    return OpenAI(api_key=get_api_key())


def ai_homework_help(text, model):
    vocab_context = "\n".join(f"- {thai}: {english}" for _, thai, _, english, *_ in load_cards()[:80])
    prompt = f"""
You are a patient Thai tutor for a beginner.
Help with the homework without simply doing everything unexplained.

Student homework:
{text}

Known vocabulary:
{vocab_context or "No saved vocabulary yet."}

Return:
1. A beginner-friendly explanation.
2. Important vocabulary with romanization and English.
3. Grammar or sentence pattern notes.
4. A corrected answer if the student included an attempt.
5. Three small practice prompts.
Keep the tone encouraging and concrete.
"""
    response = openai_client().responses.create(model=model, input=prompt)
    return response.output_text


def transcribe_audio(uploaded_file):
    audio_bytes = uploaded_file.getvalue()
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = uploaded_file.name
    result = openai_client().audio.transcriptions.create(
        model=TRANSCRIBE_MODEL,
        file=audio_file,
        language="th",
        prompt="Thai language learning audio. Preserve Thai script when possible.",
    )
    return result.text


def explain_transcript(transcript, model):
    prompt = f"""
You are a Thai listening coach for a beginner.
Analyze this Thai transcript:

{transcript}

Give:
1. Natural English meaning.
2. Word-by-word Thai vocabulary with romanization.
3. What to listen for next time.
4. A short quiz with answer key.
"""
    response = openai_client().responses.create(model=model, input=prompt)
    return response.output_text


def render_vocab_tab():
    st.subheader("Vocabulary and spaced repetition")
    col1, col2 = st.columns([1, 1])

    with col1:
        st.write("Upload CSV/TSV rows: `thai, romanization, english, category, notes`.")
        upload = st.file_uploader("Upload vocab list", type=["csv", "tsv", "txt"])
        if upload and st.button("Import uploaded vocab"):
            parse_vocab_upload(upload)
            st.success("Vocabulary imported.")
            st.rerun()

        if st.button("Load sample vocab"):
            for row in SAMPLE_WORDS:
                add_card(*row)
            st.success("Sample words added.")
            st.rerun()

    with col2:
        with st.form("add_card"):
            thai = st.text_input("Thai")
            romanization = st.text_input("Romanization")
            english = st.text_input("English")
            category = st.text_input("Category", value="custom")
            notes = st.text_area("Notes")
            if st.form_submit_button("Add card") and thai and english:
                add_card(thai, romanization, english, category, notes)
                st.success("Card added.")
                st.rerun()

    due_cards = load_cards(only_due=True)
    all_cards = load_cards()
    st.metric("Total cards", len(all_cards))
    st.metric("Due today", len(due_cards))

    st.divider()
    st.subheader("Review")
    if not due_cards:
        st.info("Nothing due right now. Add cards or come back tomorrow.")
    else:
        card = due_cards[0]
        _, thai, romanization, english, category, notes, *_ = card
        with st.container(border=True):
            st.markdown(f"## {thai}")
            st.caption(f"{romanization or 'No romanization'} · {category or 'uncategorized'}")
            with st.expander("Show answer"):
                st.write(english)
                if notes:
                    st.info(notes)
            cols = st.columns(3)
            if cols[0].button("Again"):
                review_card(card, "again")
                st.rerun()
            if cols[1].button("Good"):
                review_card(card, "good")
                st.rerun()
            if cols[2].button("Easy"):
                review_card(card, "easy")
                st.rerun()

    with st.expander("All cards"):
        st.dataframe(
            [
                {
                    "Thai": thai,
                    "Romanization": romanization,
                    "English": english,
                    "Category": category,
                    "Due": due_on,
                    "Interval": interval,
                }
                for _, thai, romanization, english, category, _, _, interval, _, due_on in all_cards
            ],
            use_container_width=True,
        )


def render_homework_tab(model):
    st.subheader("AI homework help")
    if not get_api_key():
        st.warning("Add your OpenAI API key in the sidebar or in `.streamlit/secrets.toml` to use AI help.")

    homework = st.text_area("Paste your Thai homework, instructions, or your attempted answer", height=220)
    if st.button("Explain my homework", type="primary", disabled=not bool(get_api_key())):
        with st.spinner("Thinking like a patient tutor..."):
            st.markdown(ai_homework_help(homework, model))


def render_audio_tab(model):
    st.subheader("Uploaded audio processing")
    if not get_api_key():
        st.warning("Add your OpenAI API key in the sidebar or in `.streamlit/secrets.toml` to transcribe audio.")

    audio = st.file_uploader("Upload Thai audio", type=["mp3", "mp4", "mpeg", "mpga", "m4a", "ogg", "wav", "webm"])
    if audio:
        st.audio(audio)

    if st.button("Transcribe and quiz me", type="primary", disabled=not bool(audio and get_api_key())):
        with st.spinner("Transcribing Thai audio..."):
            transcript = transcribe_audio(audio)
        st.markdown("### Transcript")
        st.write(transcript)
        with st.spinner("Building listening notes..."):
            st.markdown(explain_transcript(transcript, model))


def render_lessons_tab():
    st.subheader("Beginner lessons")
    lesson_titles = [title for title, *_ in LESSONS]
    choice = st.selectbox("Choose a lesson", lesson_titles)
    title, thai, english, practice = next(lesson for lesson in LESSONS if lesson[0] == choice)
    st.markdown(f"## {title}")
    st.markdown(f"### {thai}")
    st.write(english)
    st.info(practice)


def main():
    st.set_page_config(page_title="Thai Study Studio", page_icon="ท", layout="wide")
    init_db()

    st.title("Thai Study Studio")
    st.caption("AI homework help, audio transcription, and spaced repetition for beginner Thai.")

    with st.sidebar:
        st.header("Settings")
        if not has_secret_api_key():
            st.text_input("OpenAI API key", type="password", key="api_key")
        model = st.text_input("Text model", value=DEFAULT_MODEL)
        st.caption(f"Audio transcription model: `{TRANSCRIBE_MODEL}`")

    tabs = st.tabs(["Vocab + SRS", "AI homework", "Audio upload", "Lessons"])
    with tabs[0]:
        render_vocab_tab()
    with tabs[1]:
        render_homework_tab(model)
    with tabs[2]:
        render_audio_tab(model)
    with tabs[3]:
        render_lessons_tab()

    st.caption(f"Local date: {datetime.now().date().isoformat()}")


if __name__ == "__main__":
    main()
