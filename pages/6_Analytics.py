"""Analytics: the same numbers the Power BI report reads, live in the app.

Four metric tiles, the DAU trend, the language mix, the struggle list and the
provider split — then one button that writes the four CSVs Power BI consumes,
plus the health line that says whether the export is trustworthy.
"""

from __future__ import annotations

import streamlit as st

from core import config, export
from core.i18n import t
from core.ui import chips, enhance_js, hero, note, panel, section_label

lang = st.session_state.get("ui_language", config.DEFAULT_LANG)

numbers = export.headline_numbers()

hero(
    eyebrow="Phase 4 · Analytics",
    title=t("card_analytics", lang),
    subtitle=(
        "Every figure here is a query over the same event log the Power BI report "
        "reads. Refresh the export and the .pbix tells this story with the same numbers."
    ),
    pills=[
        f'{numbers["events"]} events',
        f'{numbers["sessions"]} session' + ("s" if numbers["sessions"] != 1 else ""),
        f'{numbers["learners"]} learner' + ("s" if numbers["learners"] != 1 else ""),
    ],
)

st.write("")

tiles = st.columns(4, gap="medium")
tiles[0].metric("Events", numbers["events"])
tiles[1].metric(t("ana_translations", lang), numbers["translations"])
tiles[2].metric(t("ana_cache", lang), f'{round(numbers["cache_hit_rate"] * 100)}%')
tiles[3].metric(t("ana_latency", lang), f'{numbers["avg_latency_ms"]} ms')

tiles2 = st.columns(4, gap="medium")
tiles2[0].metric(t("ana_tutor_turns", lang), numbers["tutor_turns"])
tiles2[1].metric(t("ana_refusals", lang), numbers["refusals"])
tiles2[2].metric(t("ana_quizzes", lang), numbers["quizzes"])
tiles2[3].metric("Sessions", numbers["sessions"])

st.divider()

left, right = st.columns(2, gap="large")

with left:
    section_label(t("ana_per_day", lang))
    daily = export.events_per_day()
    if daily.empty:
        note("No events yet — open a lesson or ask the tutor, then come back.")
    else:
        st.line_chart(daily.set_index("day")["events"], height=240)

with right:
    section_label(t("ana_by_lang", lang))
    by_lang = export.events_by_language()
    if by_lang.empty:
        note("No language data yet.")
    else:
        st.bar_chart(by_lang.set_index("language")["events"], height=240)

st.divider()

left, right = st.columns(2, gap="large")

with left:
    section_label(t("ana_top", lang))
    by_name = export.events_by_name()
    if by_name.empty:
        note("Nothing logged yet.")
    else:
        st.dataframe(by_name, width="stretch", hide_index=True, height=280)

with right:
    section_label(t("ana_struggle", lang) + " — " + "terms most tapped")
    terms = export.terms_most_translated()
    if terms.empty:
        note("No terms tapped yet. Open Learn and tap a glossary term.")
    else:
        st.dataframe(terms, width="stretch", hide_index=True, height=280)
        st.caption(
            "This is the table that tells a teacher which words need a better gloss. "
            "It exists because `term_glossed` carries the term in its props."
        )

st.divider()

section_label("Power BI export")
st.markdown(
    "Writes `fact_events.csv`, `fact_translations.csv`, `dim_lessons.csv` and "
    "`dim_users.csv` into `exports/`, plus `_health.json`. Power BI Desktop reads "
    "that folder as a source, so a refresh picks up all four files."
)

if st.button(t("ana_refresh", lang), type="primary"):
    health = export.run_export()
    st.session_state["export_health"] = health
    st.toast(f'Wrote {health["rows"]["fact_events"]} event rows in {health["duration_ms"]} ms')

health = st.session_state.get("export_health") or export.read_health()

if not health:
    note("No export yet this session. Press Refresh export.")
else:
    chips(
        [
            (f'rows: {health["rows"]["fact_events"]} events', "accent"),
            (f'{health["duration_ms"]} ms', "muted"),
            (f'mode: {health["provider_mode"]}', "muted"),
            (f'{health["event_types_fired"]}/{health["event_types_documented"]} event types fired', "ok"),
        ]
    )
    panel(f'Generated {health["generated_at"]}.')

    if health["warnings"]:
        for warning in health["warnings"]:
            st.warning(warning, icon="⚠️")
    else:
        st.success("Health check clean — no empty tables, no unexpected nulls.", icon="✅")

    with st.expander("Event coverage audit", expanded=False):
        st.caption(
            "Documented event names that have never fired. If a feature is not in the "
            "log, it is not measured — and this is how you catch that before an examiner does."
        )
        never = health.get("events_never_fired") or []
        if never:
            st.dataframe([{"never fired": name} for name in never], width="stretch", hide_index=True)
        else:
            st.success("Every documented event has fired at least once.")

    with st.expander("Null rate per column", expanded=False):
        st.dataframe(
            [{"column": key, "null rate": value} for key, value in health["null_rate"].items()],
            width="stretch",
            hide_index=True,
        )

if config.is_mock_mode():
    st.caption(
        "Mock mode: numbers are real, translations are labelled mock. The dashboard "
        "still fills — that is the point of logging every action."
    )

enhance_js()
