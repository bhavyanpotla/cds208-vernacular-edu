# Vernacular Education & Real-Time Translation Platform

A learning platform where a student reads a lesson in their mother tongue, taps any
term for an instant gloss, asks an AI tutor that answers in that language without
inventing facts, and is assessed on it — while every one of those actions becomes a
row in an event log that a teacher can read in Power BI.

CDS208 final project. Solo developer. Streamlit + SQLite + Sarvam AI, with a mock
provider so the whole app runs with no API key and no internet.

## Status

Phases 0–3 complete: dark glass shell with motion, language registry, database schema,
append-only event log, and a Home page that actually changes language when you switch it.

The UI is dark by default (`base = "dark"` in `.streamlit/config.toml`): a drifting
aurora background, frosted glass panels, gradient display type, and cards that tilt
in 3D toward the pointer. Every effect is CSS-first, so the page is fully readable
with JavaScript disabled and static under `prefers-reduced-motion`.

| Phase | What it adds | Status |
|---|---|---|
| 0 | Shell, config, DB, event log | done |
| 1 | Translation service + Translate page | done |
| 2 | Lessons, reader, tap-to-translate, quiz | done |
| 3 | Tutor agent, personalisation | done |
| 4 | Export pipeline + Power BI report | next |
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
pages/2_Translate.py   two-panel translation workspace with latency + provider badge
pages/3_Learn.py       reader, tap-to-translate glosses, static quiz
pages/4_Tutor.py       grounded chat tutor with context picker
pages/5_Progress.py    recommendation, per-lesson table, event breakdown
content/lessons/*.json four lessons, English + Hindi authored inline
content/glossary.json  term → per-language explanation
core/config.py         the only module that reads the environment
core/db.py             SQLite schema + connection (Postgres swap lives here)
core/events.py         log_event() — append-only analytics source of truth
core/llm.py            provider adapter: sarvam | mock, retries, 1000-char chunking
core/translate.py      translation service: memory cache → SQLite → provider → event
core/lessons.py        load/localise lessons + glossary, filling missing languages
core/quiz.py           pure scoring + progress/event recording
agents/prompts.py      every system prompt, one place
agents/tutor.py        grounded answers + honest refusal, offline and live
agents/coach.py        rule-first recommender, model only phrases the reason
agents/phrases.py      offline phrasing in all five languages
core/i18n.py           UI strings for English, Hindi, Bengali, Tamil, Telugu
core/ui.py             HTML/CSS helpers: hero, cards, provider badge
assets/styles.css      one stylesheet: dark glass theme, 3D tilt, AA contrast, 360px responsive
assets/app.js          optional pointer-tilt + parallax enhancer (zero-height iframe)
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
- Only English and Hindi are hand-authored; Tamil, Telugu and Bengali are filled by
  the translation service on first read and cached. That is deliberate, and the UI
  labels a gloss as authored or translated.
- The tutor refuses to answer outside the lesson it is grounded in. That is deliberate.
- Single local learner profile until auth lands in Phase 5.
- Tutor grounding is a lexical check against the lesson, so a question phrased with
  none of the lesson's vocabulary is treated as outside it. It errs toward refusing.
- Progress-page chrome (metric labels, table headers) is still English; the
  recommendation reason itself is localised. Full i18n sweep is Phase 5.

## License

Academic project — CDS208 coursework.
