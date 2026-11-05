"""HTML/CSS presentation helpers.

Streamlit is the shell; these functions are the finish. Every helper returns
nothing and writes one ``st.markdown`` block, so pages stay readable.
All interpolated text is escaped — user or model text must never be able to
inject markup.
"""

from __future__ import annotations

from html import escape

import streamlit as st

from core import config


def inject_css() -> None:
    """Load assets/styles.css once per rerun."""
    css_path = config.ASSETS_DIR / "styles.css"
    if not css_path.exists():  # pragma: no cover - guards a broken checkout
        return
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def hero(eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(
        '<div class="ve-hero">'
        f'<span class="ve-eyebrow">{escape(eyebrow)}</span>'
        f"<h1>{escape(title)}</h1>"
        f"<p>{escape(subtitle)}</p>"
        "</div>",
        unsafe_allow_html=True,
    )


def feature_cards(items: list[tuple[str, str]]) -> None:
    """``items`` is a list of ``(title, chip)`` pairs, e.g. ("Tutor", "Phase 3")."""
    cards = "".join(
        '<div class="ve-card">'
        f'<span class="ve-chip">{escape(chip)}</span>'
        f"<h3>{escape(title)}</h3>"
        "</div>"
        for title, chip in items
    )
    st.markdown(f'<div class="ve-grid">{cards}</div>', unsafe_allow_html=True)


def provider_badge() -> None:
    """The badge that keeps the demo honest: mock or live, never implied."""
    if config.is_mock_mode():
        st.markdown(
            '<span class="ve-badge ve-badge--mock">'
            '<span class="ve-dot"></span>Mock mode · no API key</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="ve-badge ve-badge--live">'
            '<span class="ve-dot"></span>Live · Sarvam AI</span>',
            unsafe_allow_html=True,
        )


def note(text: str) -> None:
    st.markdown(f'<p class="ve-note">{escape(text)}</p>', unsafe_allow_html=True)


def section_label(text: str) -> None:
    st.markdown(f'<p class="ve-section">{escape(text)}</p>', unsafe_allow_html=True)
