"""Tutor: a chat that answers in the learner's language and admits its limits.

The context picker is not decoration — the tutor is grounded in one segment of
one lesson, and the answer says so. Ask something the lesson does not cover and
it refuses, in the learner's language, instead of inventing a fact.
"""

from __future__ import annotations

import streamlit as st

from agents import phrases
from agents import tutor as tutor_agent
from core import config, events, lessons
from core.i18n import t
from core.ui import chips, enhance_js, hero, note, section_label

lang = st.session_state.get("ui_language", config.DEFAULT_LANG)
user_id = st.session_state.get("user_id")
events.log_event("page_viewed", page="tutor")

catalogue = lessons.all_lessons()

hero(
    eyebrow="Phase 3 · Agentic tutoring",
    title=phrases.p("ask_title", lang),
    subtitle=(
        "Answers come from the segment you are reading, in your language. When the "
        "lesson does not cover something, the tutor says so instead of guessing."
    ),
    pills=[
        t("mock_mode", lang) if config.is_mock_mode() else "Sarvam AI · live",
        "grounded",
        "refuses to invent",
    ],
)

st.write("")

pick_lesson, pick_segment = st.columns([2, 2], gap="large")
lesson_id = pick_lesson.selectbox(
    t("learn_lessons", lang),
    options=[item["id"] for item in catalogue],
    format_func=lambda lid: lessons.title(lessons.get(lid) or {}, lang, user_id),
    key="tutor_lesson",
)
lesson = lessons.get(lesson_id)
assert lesson is not None

segment_ids = [item["id"] for item in lesson["segments"]]
segment_id = pick_segment.selectbox(
    phrases.p("context", lang),
    options=segment_ids,
    format_func=lambda sid: f"{sid} · "
    + lessons.segment_text(
        lesson, lessons.segment(lesson, sid) or lesson["segments"][0], lang, user_id
    )[:60],
    key="tutor_segment",
)
segment = lessons.segment(lesson, segment_id)

if st.session_state.get("tutor_ctx") != (lesson_id, segment_id):
    st.session_state["tutor_ctx"] = (lesson_id, segment_id)
    st.session_state["tutor_msgs"] = []
    st.session_state["tutor_grounded"] = []

section_label(phrases.p("context", lang))
note(
    f"{lessons.title(lesson, lang, user_id)} — "
    f"{lessons.segment_text(lesson, segment, lang, user_id)}"
)

history: list[dict[str, str]] = st.session_state.setdefault("tutor_msgs", [])

st.divider()

if not history:
    note(
        "Ask about the segment above. Try something it answers, then try something it "
        "cannot — the second answer is the one worth watching."
    )

for message in history:
    with st.chat_message(message["role"]):
        st.write(message["text"])
        if message["role"] == "assistant" and message.get("meta"):
            chips(message["meta"])

quick = st.columns(2)
if quick[0].button(phrases.p("simpler", lang), width="stretch"):
    st.session_state["tutor_pending"] = "Please explain this segment in simpler words."
if quick[1].button(phrases.p("example", lang), width="stretch"):
    st.session_state["tutor_pending"] = "Give me one example of what this segment describes."

typed = st.chat_input(phrases.p("ask_title", lang))
question = typed or st.session_state.pop("tutor_pending", None)

if question:
    history.append({"role": "user", "text": question})
    with st.chat_message("user"):
        st.write(question)

    result = tutor_agent.answer(
        question,
        lesson=lesson,
        segment=segment,
        lang=lang,
        history=[{"role": m["role"], "content": m["text"]} for m in history[:-1]],
        user_id=user_id,
    )

    meta: list[tuple[str, str]] = []
    if result["provider"] == "sarvam":
        meta.append(("Sarvam AI", "accent"))
    elif result["provider"] == "mock":
        meta.append((t("mock_mode", lang), "warn"))
    meta.append(
        (phrases.p("grounded", lang), "ok")
        if result["grounded"]
        else (phrases.p("outside", lang), "warn")
    )
    if result["degraded"]:
        meta.append(("fell back offline", "warn"))

    with st.chat_message("assistant"):
        st.write_stream(word for word in result["text"].split(" ") for word in (word + " ",))
        chips(meta)

    history.append({"role": "assistant", "text": result["text"], "meta": meta})

st.divider()
with st.expander("What this agent will not do", expanded=False):
    st.markdown(
        "- It will not answer from outside the lesson you selected. Ask it something the "
        "lesson does not cover and it says so, then gives one hint — that is the design, "
        "not a failure.\n"
        "- It will not claim the lesson said something it did not. In live mode the "
        "segment is inside the system prompt with an explicit anti-invention rule; in "
        "mock mode the answer is assembled from the lesson text itself.\n"
        "- Grounding is checked lexically, so a question phrased with none of the "
        "lesson's vocabulary is treated as outside it. That errs toward refusing."
    )
    if config.is_mock_mode():
        st.caption(
            "Mock mode: replies are built offline from the lesson and labelled. Add "
            "SARVAM_API_KEY and the same question goes to sarvam-m instead."
        )

enhance_js()
