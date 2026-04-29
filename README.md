# Thai Study Studio

A Thai learning app with two deployable versions:

- `index.html`: a static browser app for GitHub Pages.
- `streamlit_app.py`: a backend app with AI homework help, audio upload processing, and SQLite spaced repetition.

## Run the static app

Open `index.html` in a browser, or start a simple local server:

```bash
python3 -m http.server 5173
```

Then visit `http://localhost:5173`.

## Vocab Import Format

Use CSV or TSV rows in this order:

```text
thai,romanization,english,category,notes
สวัสดี,sawatdee,hello,greetings,polite greeting
```

The app stores words and practice counts in browser local storage.

## Run the Streamlit app

Install dependencies:

```bash
pip install -r requirements.txt
```

Start Streamlit:

```bash
streamlit run streamlit_app.py
```

The Streamlit version stores spaced-repetition cards in `thai_study.db`.

The Streamlit version includes:

- expanded beginner lessons with teaching notes, patterns, detailed examples, detail sections, drills, and audio buttons
- hover tooltips for known Thai words in lessons, conversation practice, SRS review, homework output, and audio transcripts
- slow conversation practice with normal/slow playback and AI coach replies
- AI homework help
- uploaded audio transcription and listening notes
- SQLite spaced repetition

## OpenAI API Key

For local Streamlit use, create `.streamlit/secrets.toml`:

```toml
OPENAI_API_KEY = "sk-your-api-key-here"
```

For Streamlit Community Cloud, add the same value in the app's **Secrets** settings.

## Deploy

### GitHub Pages

Use GitHub Pages for the static version:

1. Push `index.html`, `styles.css`, `app.js`, and `README.md` to GitHub.
2. Go to **Settings → Pages**.
3. Choose **Deploy from a branch**.
4. Select `main` and `/root`.

### Streamlit Community Cloud

Use Streamlit Community Cloud for the AI/backend version:

1. Push all files to GitHub.
2. Go to `https://share.streamlit.io`.
3. Create an app from your GitHub repo.
4. Set the entrypoint file to `streamlit_app.py`.
5. Add `OPENAI_API_KEY` in Secrets.
