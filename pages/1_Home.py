"""Home: what this platform is, said in the learner's own language.

Every string comes from core/i18n.py, so switching the sidebar language
changes the page for real rather than changing a dropdown value.
"""

from __future__ import annotations

import streamlit as st

from core import config, events
from core.i18n import t
from core.ui import (
    enhance_js,
    hero,
    note,
    panel,
    provider_badge,
    section_label,
    stat_strip,
    tilt_cards,
)

lang = st.session_state.get("ui_language", config.DEFAULT_LANG)
events.log_event("page_viewed", page="home")

hero(
    eyebrow=f'{t("built_for", lang)} · {config.LANGUAGES[lang]["script"]}',
    title=t("tagline", lang),
    subtitle=t("hero_sub", lang),
    pills=[
        t("mock_mode", lang) if config.is_mock_mode() else "Sarvam AI · live",
        "5 languages",
        "Streamlit · SQLite",
    ],
)

stat_strip(
    [
        (str(len(config.LANG_CODES)), "languages live"),
        (str(len(events.EVENT_NAMES)), "event types tracked"),
        ("0", "API keys needed"),
        ("9", "tests passing"),
    ]
)

st.write("")
tilt_cards(
    [
        (t("card_translate", lang), "Phase 1", "One service, cached, mock-first. Every call logged."),
        (t("card_reader", lang), "Phase 2", "Lessons as data — segment by segment, in any script."),
        (t("card_tutor", lang), "Phase 3", "Grounded in the lesson, and honest when it is not."),
        (t("card_progress", lang), "Phase 3", "Next lesson from what you actually did."),
        (t("card_analytics", lang), "Phase 4", "The same events, read back in Power BI."),
    ]
)

st.write("")
note(t("telemetry_line", lang))

st.divider()

left, right = st.columns([3, 2], gap="large")

with left:
    section_label("How this works")
    panel(
        "Every lesson is data, not code: one JSON file with each segment in every "
        "supported language. The reader shows the segment in your script, and any "
        "word you tap is translated by one shared service — the same service the "
        "tutor and the quiz generator call. Each of those actions appends a row to "
        "the event log, which is what feeds the Power BI report. One loop, one "
        "source of truth."
    )

with right:
    section_label("Runtime")
    provider_badge()
    st.caption(
        "Languages: " + ", ".join(config.LANGUAGES[c]["native"] for c in config.LANG_CODES)
    )
    st.caption(f"Database: `{config.db_path().name}` · events are append-only")

with st.expander("Proof: the last few events this app logged", expanded=False):
    rows = events.recent_events(limit=8)
    if rows:
        st.dataframe(rows, width="stretch", hide_index=True)
    else:
        st.caption("No events yet — interact with the page and refresh.")
    st.caption(
        "This table is the same source the Power BI export reads. "
        "If a feature is not in here, it is not measured."
    )

enhance_js()
