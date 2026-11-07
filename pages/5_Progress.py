"""Progress: what this learner has done, and what to do next.

The recommendation is the visible part of the personalisation agent. The reason
is written in the learner's language, and the rule engine behind it works with
an empty database, a dead provider or a model that returns nonsense.
"""

from __future__ import annotations

import streamlit as st

from agents import coach
from core import config, db, events, lessons
from core.i18n import t
from core.ui import chips, enhance_js, hero, note, panel, section_label

lang = st.session_state.get("ui_language", config.DEFAULT_LANG)
user_id = st.session_state.get("user_id")
events.log_event("page_viewed", page="progress")

summary = db.progress_summary(user_id) if user_id else {
    "lessons_touched": 0,
    "quiz_passed": 0,
    "avg_score": 0,
}
event_counts = events.event_counts()

hero(
    eyebrow="Phase 3 · Personalisation",
    title=t("nav_progress", lang),
    subtitle=(
        "Everything here is read back from the event log and the progress table — the "
        "same rows the Power BI report will use in Phase 4."
    ),
    pills=[
        f'{summary["lessons_touched"]} lessons touched',
        f'{summary["quiz_passed"]} passed',
        f'{sum(event_counts.values())} events',
    ],
)

st.write("")

metrics = st.columns(4, gap="medium")
metrics[0].metric("Lessons touched", summary["lessons_touched"])
metrics[1].metric("Quizzes passed", summary["quiz_passed"])
metrics[2].metric("Average score", f'{summary["avg_score"]}%')
metrics[3].metric("Events logged", sum(event_counts.values()))

st.write("")
section_label("Recommended next")

recommendation = coach.recommend(user_id, lang)
next_lesson = lessons.get(recommendation["next_lesson_id"])

chip_items: list[tuple[str, str]] = [
    (f'difficulty: {recommendation["difficulty"]}', "accent"),
    (f'source: {recommendation["source"]}', "muted"),
]
if next_lesson:
    chip_items.append((f'{next_lesson["subject"]} · class {next_lesson["grade"]}', "muted"))
chips(chip_items)

panel(recommendation["reason"])

if next_lesson:
    st.caption(
        f'Next: **{lessons.title(next_lesson, lang, user_id)}** · focus on '
        + ", ".join(recommendation["focus_terms"] or lessons.key_terms(next_lesson)[:3])
    )

if st.button("Recompute recommendation"):
    st.session_state.pop("_progress_refresh", None)
    st.rerun()

st.divider()

section_label("Per lesson")

rows = []
for lesson in lessons.all_lessons():
    row = db.lesson_progress(user_id, lesson["id"]) if user_id else None
    rows.append(
        {
            "lesson": lessons.title(lesson, lang, user_id),
            "subject": lesson["subject"],
            "grade": lesson["grade"],
            "status": (row or {}).get("status") or "not started",
            "score": f'{round(float((row or {}).get("score") or 0) * 100)}%'
            if (row or {}).get("score") is not None
            else "—",
        }
    )
st.dataframe(rows, width="stretch", hide_index=True)

section_label("What the log says")
if event_counts:
    st.dataframe(
        [{"event": name, "count": count} for name, count in event_counts.items()],
        width="stretch",
        hide_index=True,
    )
else:
    note("No events yet. Read a lesson, tap a term, or ask the tutor a question.")

with st.expander("Why the recommender cannot break", expanded=False):
    st.markdown(
        "- Rules first: a failed quiz means revisit the same lesson at easy difficulty; "
        "otherwise the earliest unread lesson at core; if everything is passed, the "
        "weakest score at stretch.\n"
        "- The model only ever *phrases* that plan. Its id is validated against the "
        "catalogue, and any unparsable reply falls straight back to the rules.\n"
        "- Consequence: with an empty database, no API key and no internet, this page "
        "still recommends a real lesson with a real reason."
    )
    if config.is_mock_mode():
        st.caption(
            "Mock mode: reasons are authored in English and Hindi and machine-translated "
            "and cached for the other three languages."
        )

enhance_js()
