"""Translate: the Phase 1 workspace — two panels, honest metadata.

Source on the left, result on the right. Every call goes through
core.translate, so the cache, the latency figure and the event row are the
same ones the reader and the tutor will use in Phase 2 and 3.
"""

from __future__ import annotations

import streamlit as st

from core import config, db, events
from core import translate as translator
from core.i18n import t
from core.ui import chips, enhance_js, hero, note, section_label

lang = st.session_state.get("ui_language", config.DEFAULT_LANG)
events.log_event("page_viewed", page="translate")

EXAMPLES = {
    "en-IN": "The plant makes food from sunlight, water and air.",
    "hi-IN": "पौधे सूर्य के प्रकाश, पानी और हवा से भोजन बनाते हैं।",
    "te-IN": "మొక్క సూర్యరశ్మి, నీరు మరియు గాలి నుండి ఆహారాన్ని తయారు చేస్తుంది.",
    "ta-IN": "தாவரம் சூரிய ஒளி, நீர் மற்றும் காற்றிலிருந்து உணவை உருவாக்குகிறது.",
    "bn-IN": "গাছ সূর্যালোক, জল ও বাতাস থেকে খাদ্য তৈরি করে।",
}

hero(
    eyebrow="Phase 1 · Translation core",
    title=t("tr_title", lang),
    subtitle=(
        "One service, called by every surface in the app. Memory cache, then SQLite, "
        "then the provider — and every call leaves an event behind."
    ),
    pills=[
        t("mock_mode", lang) if config.is_mock_mode() else "Sarvam AI · live",
        "cached",
        "logged",
    ],
)

st.write("")

col_src, col_tgt = st.columns(2, gap="large")

with col_src:
    section_label(t("tr_source_label", lang))
    source_lang = st.selectbox(
        "Source language",
        options=config.LANG_CODES,
        index=config.LANG_CODES.index(lang),
        format_func=lambda code: config.LANGUAGES[code]["native"],
        key="tr_src",
        label_visibility="collapsed",
    )
    if st.button(t("tr_example", lang), width="stretch"):
        st.session_state["tr_text"] = EXAMPLES.get(source_lang, EXAMPLES["en-IN"])
    text = st.text_area(
        "Text to translate",
        height=190,
        max_chars=2000,
        key="tr_text",
        label_visibility="collapsed",
        placeholder="Type or paste a sentence…",
    )
    counter, action = st.columns([1, 1])
    counter.caption(f"{len(text)}/2000 chars")
    go = action.button(t("tr_button", lang), type="primary", width="stretch")

with col_tgt:
    section_label(t("tr_result", lang))
    target_lang = st.selectbox(
        "Target language",
        options=config.LANG_CODES,
        index=1,
        format_func=lambda code: config.LANGUAGES[code]["native"],
        key="tr_tgt",
        label_visibility="collapsed",
    )
    result_slot = st.container()

if go:
    if not text.strip():
        st.toast("Nothing to translate — type something first.")
    else:
        st.session_state["tr_last"] = translator.translate(
            text,
            source=source_lang,
            target=target_lang,
            user_id=st.session_state.get("user_id"),
            context="translate_page",
        )

result = st.session_state.get("tr_last")

with result_slot:
    if not result:
        note(
            "The translation appears here. Nothing leaves your machine until you "
            "press the button."
        )
    else:
        provider = result["provider"]
        pair = (
            f'{config.LANGUAGES[result["source"]]["label"]} → '
            f'{config.LANGUAGES[result["target"]]["label"]}'
            if "source" in result
            else f'{config.LANGUAGES[source_lang]["label"]} → '
            f'{config.LANGUAGES[target_lang]["label"]}'
        )
        chip_items: list[tuple[str, str]] = []
        if provider == "cache":
            chip_items.append((t("tr_cached", lang), "ok"))
        elif provider == "sarvam":
            chip_items.append(("Sarvam AI", "accent"))
        elif provider == "mock":
            chip_items.append((t("mock_mode", lang), "warn"))
        else:
            chip_items.append(("Same language", "muted"))
        chip_items.append((f"{result['latency_ms']} ms", "muted"))
        chip_items.append((pair, "muted"))
        if result.get("degraded"):
            chip_items.append(("degraded to mock", "warn"))
        chips(chip_items)

        st.code(result["text"], language=None, wrap_lines=True)

        if result.get("degraded"):
            st.warning(
                "The provider call failed, so this is a mock result. "
                f"Reason: {result.get('error') or 'unknown'}",
                icon="⚠️",
            )
        elif provider == "mock":
            st.caption(
                "Mock mode: no API key configured. Add SARVAM_API_KEY to .env and this "
                "same click returns real text from Sarvam — nothing else changes."
            )
        elif provider == "cache":
            st.caption(
                "This pair was already translated, so no provider call was made. "
                "The latency above is the original call's, not this one's."
            )

st.divider()

stats = db.translation_stats()
if stats["total"]:
    left, right = st.columns(2, gap="large")
    left.metric("Translations stored", stats["total"])
    right.metric("Average latency", f"{stats['avg_latency_ms']} ms")

with st.expander(t("tr_recent", lang), expanded=False):
    rows = db.recent_translations(limit=10)
    if rows:
        st.dataframe(rows, width="stretch", hide_index=True)
    else:
        st.caption("Nothing yet — translate a sentence above.")
    st.caption(
        "Rows come from the `translations` table. A cache hit writes an event, not a row."
    )

enhance_js()
