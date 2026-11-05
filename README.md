# Vernacular Education & Real-Time Translation Platform

A learning platform where a student reads a lesson in their mother tongue, taps any
term for an instant gloss, asks an AI tutor that answers in that language without
inventing facts, and is assessed on it — while every one of those actions becomes a
row in an event log that a teacher can read in Power BI.

CDS208 final project. Solo developer. Streamlit + SQLite + Sarvam AI, with a mock
provider so the whole app runs with no API key and no internet.

## Status

Phase 0 complete: styled shell, language registry, database schema, append-only
event log, and a Home page that actually changes language when you switch it.

| Phase | What it adds | Status |
|---|---|---|
| 0 | Shell, config, DB, event log | done |
| 1 | Translation service + Translate page | next |
| 2 | Lessons, reader, tap-to-translate, quiz | planned |
| 3 | Tutor agent, personalisation | planned |
| 4 | Export pipeline + Power BI report | planned |
| 5 | Polish, accessibility, deployment | planned |

## Run it

```bash
git clone https://github.com/<your-handle>/cds208-vernacular-edu.git
cd cds208-vernacular-edu
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

No `.env` needed. With no `SARVAM_API_KEY` the sidebar shows a **Mock mode** badge and
every AI path returns a labelled mock result — nothing silently pretends to be real.

To use the real provider:

```bash
cp .env.example .env    # then put your key in SARVAM_API_KEY
```

## Tests

```bash
pip install ruff pytest
ruff check .
python -m pytest
```

CI runs both on every push (`.github/workflows/ci.yml`).

## Structure

```
app.py                 entry: page config, CSS, session bootstrap, navigation
pages/1_Home.py        Home surface
core/config.py         the only module that reads the environment
core/db.py             SQLite schema + connection (Postgres swap lives here)
core/events.py         log_event() — append-only analytics source of truth
core/i18n.py           UI strings for English, Hindi, Bengali, Tamil, Telugu
core/ui.py             HTML/CSS helpers: hero, cards, provider badge
assets/styles.css      one stylesheet, WCAG AA contrast, 360px responsive
tests/                 config, i18n, event-log and schema tests
```

Two rules hold the design together: services never call Streamlit APIs (so they stay
testable), and pages never call the AI provider directly (always through a service).

## Languages

English, हिन्दी, বাংলা, தமிழ், తెలుగు — five done properly rather than eleven done
badly. Adding a sixth is one entry in `core/config.py` plus its strings in
`core/i18n.py`.

## Known limitations

- Speech (STT/TTS) is on the roadmap, not in the build — the text path is the product.
- Four lessons, not a curriculum; this is a demonstration of the loop, not a content library.
- The tutor refuses to answer outside the lesson it is grounded in. That is deliberate.
- Single local learner profile until auth lands in Phase 5.

## License

Academic project — CDS208 coursework.
