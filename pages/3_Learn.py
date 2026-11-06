"""Learn: the mother-tongue reader, tap-to-translate, and the static quiz.

The reader is the surface the whole product exists for. A lesson is data; the
segment is shown in the learner's language — authored where we wrote it, filled
by the translation service where we did not — and any term can be tapped for a
gloss in the same language. Every tap and every answer is an event.
"""

from __future__ import annotations

import streamlit as st

from core import config, db, events, lessons, quiz
from core.i18n import t
from core.ui import chips, enhance_js, hero, note, panel, section_label

lang = st.session_state.get("ui_language", config.DEFAULT_LANG)
user_id = st.session_state.get("user_id")
events.log_event("page_viewed", page="learn")

catalogue = lessons.all_lessons()

hero(
    eyebrow="Phase 2 · Vernacular reader",
    title=t("learn_lessons", lang),
    subtitle=(
        "Four lessons, read in your own script. Tap any term for its meaning — "
        "authored in English and Hindi, filled by the translation service for the rest."
    ),
    pills=[f"{len(catalogue)} lessons", f"{len(lessons.glossary_terms())} glossary terms", t("mock_mode", lang) if config.is_mock_mode() else "Sarvam AI · live"],
)

st.write("")

if not catalogue:  # pragma: no cover - guards a broken checkout
    st.error("No lessons found in content/lessons. Check the JSON files.")
    st.stop()

picker_lang, picker_lesson = st.columns([1, 2], gap="large")
read_lang = picker_lang.selectbox(
    t("learn_read_in", lang),
    options=config.LANG_CODES,
    index=config.LANG_CODES.index(lang),
    format_func=lambda code: config.LANGUAGES[code]["native"],
    key="learn_lang",
)
lesson_id = picker_lesson.selectbox(
    t("learn_lessons", lang),
    options=[item["id"] for item in catalogue],
    format_func=lambda lid: lessons.title(lessons.get(lid) or {}, read_lang, user_id),
    key="learn_lesson",
)

lesson = lessons.get(lesson_id)
assert lesson is not None  # selectbox is built from this catalogue

seen = st.session_state.get("_learn_seen")
if seen != (lesson_id, read_lang):
    st.session_state["_learn_seen"] = (lesson_id, read_lang)
    events.log_event(
        "lesson_opened",
        lesson_id=lesson_id,
        subject=lesson.get("subject"),
        grade=lesson.get("grade"),
        read_lang=read_lang,
    )

progress = db.lesson_progress(user_id, lesson_id) if user_id else None
head_chips: list[tuple[str, str]] = [
    (f'{lesson.get("subject", "lesson")} · class {lesson.get("grade", "-")}', "muted"),
    (f'{len(lesson["segments"])} segments', "muted"),
]
if progress:
    head_chips.append(
        (
            f'last: {progress["status"]} · {round(float(progress["score"] or 0) * 100)}%',
            "ok" if progress["status"] == "quiz_passed" else "muted",
        )
    )
chips(head_chips)

col_read, col_side = st.columns([3, 2], gap="large")

with col_read:
    for item in lesson["segments"]:
        text = lessons.segment_text(lesson, item, read_lang, user_id)
        panel(text)
        terms = item.get("key_terms", [])
        if terms:
            term_cols = st.columns(len(terms))
            for index, term in enumerate(terms):
                if term_cols[index].button(term, key=f"term_{lesson_id}_{item['id']}_{index}", width="stretch"):
                    entry = lessons.glossary_entry(term, read_lang, user_id)
                    st.session_state["gloss"] = entry
                    events.log_event(
                        "term_glossed",
                        lesson_id=lesson_id,
                        segment_id=item["id"],
                        term=term,
                        read_lang=read_lang,
                        authored=entry["authored"] if entry else "missing",
                    )
        st.write("")

with col_side:
    section_label(t("learn_glossary", lang))
    entry = st.session_state.get("gloss")
    if not entry:
        note(t("learn_tap", lang))
    else:
        chips(
            [
                (entry["term"], "accent"),
                ("authored" if entry["authored"] == "yes" else "translated", "muted"),
            ]
        )
        panel(entry["meaning"])
        st.caption(
            "Authored glosses are hand-written. A 'translated' gloss was filled by the "
            "translation service and cached, so the next reader gets it instantly."
        )

st.divider()

with st.expander(t("learn_quiz", lang), expanded=False):
    answers: list[int | None] = []
    for index in range(len(lesson.get("quiz", []))):
        question = lessons.quiz_question(lesson, index, read_lang, user_id)
        st.markdown(f"**{index + 1}. {question['q']}**")
        choice = st.radio(
            f"q{index}",
            options=list(range(len(question["options"]))),
            format_func=lambda i, opts=question["options"]: opts[i],
            index=None,
            key=f"quiz_{lesson_id}_{index}",
            label_visibility="collapsed",
        )
        answers.append(choice)

    if st.button(t("learn_check", lang), type="primary"):
        result = quiz.score(answers, quiz.answer_key(lesson))
        quiz.record_attempt(lesson, result, user_id=user_id, lang=read_lang)
        st.session_state[f"quiz_result_{lesson_id}"] = result

    result = st.session_state.get(f"quiz_result_{lesson_id}")
    if result:
        left, right = st.columns(2)
        left.metric(
            t("learn_score", lang),
            f'{result["correct"]}/{result["total"]}',
        )
        right.metric("Percent", f'{result["percent"]}%')
        if result["passed"]:
            st.success(f'Passed — {result["percent"]}% correct. Logged as quiz_passed.')
        else:
            st.info(
                f'{result["percent"]}% correct. {int(quiz.PASS_MARK * 100)}% is the pass '
                "mark — read the segments again and retake it."
            )
        for index in range(len(lesson.get("quiz", []))):
            question = lessons.quiz_question(lesson, index, read_lang, user_id)
            st.caption(
                f'{index + 1}. {question["explain"]} '
                f'(answer: {question["options"][question["answer_index"]]})'
            )

enhance_js()
