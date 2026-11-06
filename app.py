"""Entry point: page config, global CSS, session bootstrap, navigation.

Run with:  streamlit run app.py

The navigation registry grows one entry per phase — a page is registered only
when it actually works, so nothing in the sidebar is a placeholder.
"""

from __future__ import annotations

import streamlit as st

from core import config, db, events
from core.i18n import t
from core.ui import aurora, inject_css, provider_badge

st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)


def bootstrap() -> None:
    """Create the schema and session once per browser session, not per rerun."""
    if not st.session_state.get("_ve_bootstrapped"):
        db.init_db()
        events.ensure_session()
        st.session_state["_ve_bootstrapped"] = True
        events.log_event("app_opened", provider=config.provider_mode())
    st.session_state.setdefault("ui_language", config.DEFAULT_LANG)


def sidebar_controls() -> str:
    """Language picker and the honest provider badge. Returns the UI language."""
    with st.sidebar:
        st.markdown(
            f'<p class="ve-brand">{config.APP_SHORT}</p>', unsafe_allow_html=True
        )
        lang = st.selectbox(
            t("choose_language", st.session_state["ui_language"]),
            options=config.LANG_CODES,
            format_func=lambda code: config.LANGUAGES[code]["native"],
            key="ui_language",
        )
        provider_badge()
    return lang


def main() -> None:
    bootstrap()
    inject_css()
    aurora()
    lang = sidebar_controls()

    if st.session_state.get("_ve_last_lang") != lang:
        st.session_state["_ve_last_lang"] = lang
        db.set_ui_language(st.session_state["user_id"], lang)
        events.log_event("ui_language_changed", lang=lang, to=lang)

    pages = [
        st.Page(
            "pages/1_Home.py",
            title=t("nav_home", lang),
            icon=":material/home:",
            default=True,
            url_path="home",
        ),
    ]
    st.navigation(pages, position="sidebar").run()


main()
