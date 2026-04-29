import csv
import html
import io
import json
import sqlite3
from datetime import date, datetime, timedelta

import streamlit as st
import streamlit.components.v1 as components


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
    {
        "title": "Greetings and Politeness",
        "goal": "Greet people and add the polite ending that makes beginner Thai sound warm.",
        "teach": "Thai often uses a polite particle at the end of short phrases. Many female speakers use ค่ะ, many male speakers use ครับ. You can use สวัสดี for hello and goodbye.",
        "pattern": "Phrase + ค่ะ/ครับ",
        "vocab": [
            ("สวัสดี", "sawatdee", "hello / goodbye"),
            ("ขอบคุณ", "khop khun", "thank you"),
            ("ค่ะ", "kha", "polite particle"),
            ("ครับ", "khrap", "polite particle"),
        ],
        "examples": [
            ("สวัสดีค่ะ", "sawatdee kha", "Hello."),
            ("ขอบคุณครับ", "khop khun khrap", "Thank you."),
            ("สวัสดี คุณสบายดีไหม", "sawatdee, khun sabai dee mai", "Hello, how are you?"),
        ],
        "drills": ["Say hello politely twice.", "Thank someone using ค่ะ or ครับ.", "Change the particle and listen again."],
    },
    {
        "title": "Introductions",
        "goal": "Say your name and ask someone else's name.",
        "teach": "The word ชื่อ means name or to be called. Thai often drops 'am/is/are', so ฉันชื่อ Anna literally works as 'I named Anna'.",
        "pattern": "ฉัน/ผม + ชื่อ + name",
        "vocab": [("ฉัน", "chan", "I"), ("ผม", "phom", "I"), ("ชื่อ", "chue", "name"), ("อะไร", "arai", "what")],
        "examples": [
            ("ฉันชื่อแอนนา", "chan chue Anna", "My name is Anna."),
            ("คุณชื่ออะไรคะ", "khun chue arai kha", "What is your name?"),
            ("ยินดีที่ได้รู้จัก", "yin dee tee dai ruu jak", "Nice to meet you."),
        ],
        "drills": ["Put your own name into ฉันชื่อ...", "Ask คุณชื่ออะไรคะ.", "Reply with only your name, then a full sentence."],
    },
    {
        "title": "Yes, No, and Not",
        "goal": "Answer simple questions without overthinking grammar.",
        "teach": "ใช่ means yes/correct. ไม่ goes before a verb or adjective to make it negative. ไม่ใช่ is 'not correct' or 'no' when denying a statement.",
        "pattern": "ไม่ + verb/adjective",
        "vocab": [("ใช่", "chai", "yes / correct"), ("ไม่", "mai", "not"), ("ไม่ใช่", "mai chai", "no / not correct"), ("ได้", "dai", "can / okay")],
        "examples": [("ใช่ค่ะ", "chai kha", "Yes."), ("ไม่ใช่ครับ", "mai chai khrap", "No / not correct."), ("ไม่ได้", "mai dai", "Cannot / not okay.")],
        "drills": ["Turn ใช่ into ไม่ใช่.", "Say cannot.", "Answer yes politely."],
    },
    {
        "title": "Numbers 1-10",
        "goal": "Recognize numbers for prices, quantities, and time.",
        "teach": "Thai numbers combine regularly after ten. Start by making 1-10 automatic, then prices become much easier.",
        "pattern": "number + classifier/thing",
        "vocab": [("หนึ่ง", "nueng", "one"), ("สอง", "song", "two"), ("สาม", "saam", "three"), ("สิบ", "sip", "ten")],
        "examples": [("หนึ่ง สอง สาม", "nueng song saam", "One, two, three."), ("ห้าบาท", "haa baat", "Five baht."), ("สิบบาท", "sip baat", "Ten baht.")],
        "drills": ["Count from 1 to 10.", "Say 5 baht.", "Say 10 baht and listen twice."],
    },
    {
        "title": "Telling Time",
        "goal": "Ask what time it is and understand simple hour answers.",
        "teach": "กี่ means how many. โมง is an hour marker in many time expressions. แล้ว adds the feeling of 'already/now' in กี่โมงแล้ว.",
        "pattern": "กี่โมงแล้ว / number + โมง",
        "vocab": [("เวลา", "welaa", "time"), ("กี่โมง", "gee mong", "what time"), ("โมง", "mong", "o'clock"), ("นาที", "naa-thee", "minute")],
        "examples": [("กี่โมงแล้ว", "gee mong laew", "What time is it?"), ("สามโมง", "saam mong", "Three o'clock."), ("ห้านาที", "haa naa-thee", "Five minutes.")],
        "drills": ["Ask what time it is.", "Say three o'clock.", "Say five minutes."],
    },
    {
        "title": "Days of the Week",
        "goal": "Talk about today, tomorrow, and yesterday.",
        "teach": "วัน means day. Add นี้ for this, พรุ่งนี้ for tomorrow, and เมื่อวาน for yesterday.",
        "pattern": "วันนี้ / พรุ่งนี้ / เมื่อวาน + sentence",
        "vocab": [("วัน", "wan", "day"), ("วันนี้", "wan nee", "today"), ("พรุ่งนี้", "phrung nee", "tomorrow"), ("เมื่อวาน", "muea waan", "yesterday")],
        "examples": [("วันนี้วันอะไร", "wan nee wan arai", "What day is today?"), ("พรุ่งนี้ฉันเรียนภาษาไทย", "phrung nee chan rian phasaa thai", "Tomorrow I study Thai."), ("เมื่อวานฉันดื่มกาแฟ", "muea waan chan duem gaa-fae", "Yesterday I drank coffee.")],
        "drills": ["Ask what day today is.", "Say you study Thai tomorrow.", "Make one sentence with วันนี้."],
    },
    {
        "title": "Colors",
        "goal": "Describe objects with color words.",
        "teach": "สี means color. Many color names start with สี. Thai adjectives usually come after nouns: shirt red, cup blue.",
        "pattern": "noun + สี + color",
        "vocab": [("สี", "see", "color"), ("สีแดง", "see daeng", "red"), ("สีฟ้า", "see faa", "sky blue"), ("สีเขียว", "see khiao", "green")],
        "examples": [("เสื้อสีแดง", "suea see daeng", "Red shirt."), ("แก้วสีฟ้า", "gaew see faa", "Blue cup."), ("บ้านสีเขียว", "baan see khiao", "Green house.")],
        "drills": ["Name three colors near you.", "Describe your shirt.", "Tap each example and repeat."],
    },
    {
        "title": "Household Items",
        "goal": "Name useful things around the home.",
        "teach": "นี่คือ means this is. อยู่ means is located. Use these to make tiny but useful home sentences.",
        "pattern": "นี่คือ + noun / noun + อยู่ + place",
        "vocab": [("บ้าน", "baan", "home / house"), ("โต๊ะ", "to", "table"), ("เก้าอี้", "gao-ee", "chair"), ("เตียง", "tiang", "bed")],
        "examples": [("นี่คือโต๊ะ", "nee khue to", "This is a table."), ("เก้าอี้อยู่ในบ้าน", "gao-ee yuu nai baan", "The chair is in the house."), ("เตียงอยู่ในห้อง", "tiang yuu nai hong", "The bed is in the room.")],
        "drills": ["Point to a table and say โต๊ะ.", "Make a sentence with บ้าน.", "List three things in your room."],
    },
    {
        "title": "Food and Drink",
        "goal": "Order and talk about simple food.",
        "teach": "ขอ is a polite way to ask for something. Thai often uses classifiers, like แก้ว for a glass/cup.",
        "pattern": "ขอ + item + number + classifier",
        "vocab": [("อาหาร", "aa-haan", "food"), ("น้ำ", "nam", "water"), ("กาแฟ", "gaa-fae", "coffee"), ("ข้าว", "khao", "rice / meal")],
        "examples": [("ขอน้ำหนึ่งแก้ว", "khor nam nueng gaew", "One glass of water, please."), ("ฉันชอบกาแฟ", "chan chop gaa-fae", "I like coffee."), ("ข้าวอร่อย", "khao a-roi", "The rice is delicious.")],
        "drills": ["Order water.", "Say you like coffee.", "Tell someone the food is delicious."],
    },
    {
        "title": "Shopping and Prices",
        "goal": "Ask how much things cost.",
        "teach": "ราคา means price. เท่าไหร่ asks how much/how many. Put them together for a survival phrase.",
        "pattern": "ราคา + เท่าไหร่",
        "vocab": [("ราคา", "raa-khaa", "price"), ("เท่าไหร่", "tao rai", "how much"), ("บาท", "baat", "baht"), ("แพง", "phaeng", "expensive")],
        "examples": [("ราคาเท่าไหร่", "raa-khaa tao rai", "How much is it?"), ("ห้าสิบบาท", "haa sip baat", "Fifty baht."), ("แพงไหม", "phaeng mai", "Is it expensive?")],
        "drills": ["Ask the price.", "Say 50 baht.", "Ask if it is expensive."],
    },
    {
        "title": "Directions",
        "goal": "Understand simple movement directions.",
        "teach": "ไป means go. ตรงไป means go straight. เลี้ยว means turn. Direction words usually come after เลี้ยว.",
        "pattern": "ตรงไป / เลี้ยว + ซ้าย/ขวา",
        "vocab": [("ไป", "pai", "go"), ("ตรงไป", "trong pai", "go straight"), ("ซ้าย", "saai", "left"), ("ขวา", "khwaa", "right")],
        "examples": [("ตรงไปค่ะ", "trong pai kha", "Go straight."), ("เลี้ยวซ้าย", "liao saai", "Turn left."), ("ไปทางขวา", "pai thaang khwaa", "Go to the right.")],
        "drills": ["Say go straight.", "Give left and right directions.", "Ask how to go somewhere."],
    },
    {
        "title": "Questions",
        "goal": "Recognize common question words.",
        "teach": "ไหม turns many statements into yes/no questions. Other question words usually sit where the answer would go.",
        "pattern": "statement + ไหม",
        "vocab": [("ไหม", "mai", "question marker"), ("ที่ไหน", "tee nai", "where"), ("เมื่อไหร่", "muea rai", "when"), ("ทำไม", "tham mai", "why")],
        "examples": [("คุณชอบไหม", "khun chop mai", "Do you like it?"), ("ห้องน้ำอยู่ที่ไหน", "hong nam yuu tee nai", "Where is the bathroom?"), ("เรียนเมื่อไหร่", "rian muea rai", "When do you study?")],
        "drills": ["Make a yes/no question.", "Ask where something is.", "Ask when class is."],
    },
]

CONVERSATION_SCENARIOS = {
    "Cafe order": [
        ("สวัสดีค่ะ รับอะไรดีคะ", "sawatdee kha, rap arai dee kha", "Hello, what would you like?"),
        ("เอากาแฟร้อนหรือเย็นคะ", "ao gaa-fae ron rue yen kha", "Would you like hot or iced coffee?"),
        ("ทั้งหมดห้าสิบบาทค่ะ", "thang mot haa sip baat kha", "That is 50 baht total."),
    ],
    "Introductions": [
        ("คุณชื่ออะไรคะ", "khun chue arai kha", "What is your name?"),
        ("คุณมาจากประเทศอะไรคะ", "khun maa jaak prathet arai kha", "What country are you from?"),
        ("ยินดีที่ได้รู้จักค่ะ", "yin dee tee dai ruu jak kha", "Nice to meet you."),
    ],
    "Directions": [
        ("ไปสถานีรถไฟฟ้ายังไงคะ", "pai sathanee rot fai faa yang ngai kha", "How do I get to the train station?"),
        ("ตรงไปแล้วเลี้ยวซ้ายค่ะ", "trong pai laew liao saai kha", "Go straight, then turn left."),
        ("อยู่ใกล้มากค่ะ", "yuu glai maak kha", "It is very nearby."),
    ],
}


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


def speak_button(text, label="Play audio", rate=0.72, key=None):
    safe_text = json.dumps(text)
    safe_label = html.escape(label)
    safe_id = html.escape(key or f"tts-{abs(hash((text, label, rate)))}")
    components.html(
        f"""
        <button id="{safe_id}" style="
            border: 1px solid #dbe4df;
            border-radius: 8px;
            background: #ffffff;
            color: #18211f;
            padding: 0.55rem 0.75rem;
            cursor: pointer;
            font: 14px system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        ">{safe_label}</button>
        <script>
        const btn = document.getElementById({json.dumps(safe_id)});
        btn.onclick = () => {{
          const utterance = new SpeechSynthesisUtterance({safe_text});
          utterance.lang = "th-TH";
          utterance.rate = {rate};
          window.speechSynthesis.cancel();
          window.speechSynthesis.speak(utterance);
        }};
        </script>
        """,
        height=44,
    )


def known_vocab_context(limit=80):
    return "\n".join(f"- {thai}: {english}" for _, thai, _, english, *_ in load_cards()[:limit])


def ai_homework_help(text, model):
    vocab_context = known_vocab_context()
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


def ai_conversation_reply(history, learner_reply, scenario, model):
    transcript = "\n".join(f"{turn['role']}: {turn['thai']} / {turn.get('english', '')}" for turn in history[-8:])
    prompt = f"""
You are a very patient Thai conversation tutor.
Scenario: {scenario}

Recent conversation:
{transcript}

Learner just replied:
{learner_reply}

Respond with exactly this format:
Thai: <one short natural Thai line>
Romanization: <beginner-friendly romanization>
English: <natural English meaning>
Coach: <one gentle correction or encouragement, under 25 words>

Keep the Thai beginner-friendly and continue the scenario slowly.
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


def render_conversation_tab(model):
    st.subheader("Slow conversation practice")
    st.write("Pick a situation, listen to the coach, reply in Thai, romanization, or English, then keep going slowly.")

    scenario_name = st.selectbox("Scenario", list(CONVERSATION_SCENARIOS.keys()))
    if "conversation_scenario" not in st.session_state or st.session_state.conversation_scenario != scenario_name:
        st.session_state.conversation_scenario = scenario_name
        st.session_state.conversation_step = 0
        st.session_state.conversation_history = []

    scenario = CONVERSATION_SCENARIOS[scenario_name]

    def add_scripted_coach_line():
        line = scenario[st.session_state.conversation_step % len(scenario)]
        st.session_state.conversation_history.append(
            {"role": "Coach", "thai": line[0], "romanization": line[1], "english": line[2], "coach": ""}
        )
        st.session_state.conversation_step += 1

    if not st.session_state.conversation_history:
        add_scripted_coach_line()

    top_cols = st.columns(3)
    if top_cols[0].button("Restart conversation"):
        st.session_state.conversation_step = 0
        st.session_state.conversation_history = []
        add_scripted_coach_line()
        st.rerun()
    if top_cols[1].button("Coach says another line"):
        add_scripted_coach_line()
        st.rerun()
    if top_cols[2].button("Add sample vocab to SRS"):
        for line in scenario:
            add_card(line[0], line[1], line[2], "conversation", f"From {scenario_name}.")
        st.success("Conversation lines added to spaced repetition.")

    for index, turn in enumerate(st.session_state.conversation_history):
        with st.chat_message("assistant" if turn["role"] == "Coach" else "user"):
            st.markdown(f"### {turn['thai']}")
            if turn.get("romanization"):
                st.caption(turn["romanization"])
            if turn.get("english"):
                st.write(turn["english"])
            if turn.get("coach"):
                st.info(turn["coach"])
            cols = st.columns([1, 1, 5])
            with cols[0]:
                speak_button(turn["thai"], "Normal", 0.72, key=f"normal-{index}")
            with cols[1]:
                speak_button(turn["thai"], "Slow", 0.48, key=f"slow-{index}")

    learner_reply = st.chat_input("Reply here")
    if learner_reply:
        st.session_state.conversation_history.append({"role": "You", "thai": learner_reply, "romanization": "", "english": "", "coach": ""})
        if get_api_key():
            with st.spinner("Coach is thinking patiently..."):
                ai_text = ai_conversation_reply(
                    st.session_state.conversation_history,
                    learner_reply,
                    scenario_name,
                    model,
                )
            parsed = {"role": "Coach", "thai": ai_text, "romanization": "", "english": "", "coach": ""}
            for line in ai_text.splitlines():
                if line.startswith("Thai:"):
                    parsed["thai"] = line.replace("Thai:", "", 1).strip()
                elif line.startswith("Romanization:"):
                    parsed["romanization"] = line.replace("Romanization:", "", 1).strip()
                elif line.startswith("English:"):
                    parsed["english"] = line.replace("English:", "", 1).strip()
                elif line.startswith("Coach:"):
                    parsed["coach"] = line.replace("Coach:", "", 1).strip()
            st.session_state.conversation_history.append(parsed)
        else:
            add_scripted_coach_line()
        st.rerun()


def render_lessons_tab():
    st.subheader("Beginner lessons")
    lesson_titles = [lesson["title"] for lesson in LESSONS]
    choice = st.selectbox("Choose a lesson", lesson_titles)
    lesson = next(item for item in LESSONS if item["title"] == choice)

    st.markdown(f"## {lesson['title']}")
    st.success(lesson["goal"])
    st.markdown("### Teaching note")
    st.write(lesson["teach"])
    st.markdown("### Pattern")
    st.code(lesson["pattern"])

    st.markdown("### Core vocabulary")
    st.dataframe(
        [{"Thai": thai, "Romanization": romanization, "English": english_text} for thai, romanization, english_text in lesson["vocab"]],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Example phrases")
    for index, (thai, romanization, english_text) in enumerate(lesson["examples"]):
        with st.container(border=True):
            left, right = st.columns([4, 1])
            with left:
                st.markdown(f"### {thai}")
                st.caption(romanization)
                st.write(english_text)
            with right:
                speak_button(thai, "Play", 0.72, key=f"lesson-{choice}-{index}")

    st.markdown("### Practice drills")
    for drill in lesson["drills"]:
        st.checkbox(drill, key=f"drill-{choice}-{drill}")

    if st.button("Add this lesson's words to SRS"):
        for thai, romanization, english_text in lesson["vocab"]:
            add_card(thai, romanization, english_text, lesson["title"], lesson["pattern"])
        st.success("Lesson vocabulary added to spaced repetition.")


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

    tabs = st.tabs(["Vocab + SRS", "Lessons", "Conversation", "AI homework", "Audio upload"])
    with tabs[0]:
        render_vocab_tab()
    with tabs[1]:
        render_lessons_tab()
    with tabs[2]:
        render_conversation_tab(model)
    with tabs[3]:
        render_homework_tab(model)
    with tabs[4]:
        render_audio_tab(model)

    st.caption(f"Local date: {datetime.now().date().isoformat()}")


if __name__ == "__main__":
    main()
