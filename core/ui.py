"""HTML builders for the dark glass surfaces, plus their render helpers.

Every builder is a pure function returning a string, so the markup can be
previewed and diffed outside Streamlit. The ``*_view`` helpers are the only
place that touches ``st``. All interpolated text is escaped — model output and
user input must never be able to inject markup.
"""

from __future__ import annotations

from html import escape

import streamlit as st

from core import config

# --------------------------------------------------------------- builders


def aurora_html() -> str:
    """The fixed background layer: gradient wash, grid, three drifting blobs."""
    return (
        '<div class="ve-aurora" aria-hidden="true">'
        '<span class="ve-blob ve-blob--a"></span>'
        '<span class="ve-blob ve-blob--b"></span>'
        '<span class="ve-blob ve-blob--c"></span>'
        "</div>"
    )


def hero_html(eyebrow: str, title: str, subtitle: str, pills: list[str] | None = None) -> str:
    pill_markup = "".join(
        f'<span class="ve-pill{" ve-pill--accent" if index == 0 else ""}">{escape(p)}</span>'
        for index, p in enumerate(pills or [])
    )
    foot = f'<div class="ve-hero-foot">{pill_markup}</div>' if pill_markup else ""
    return (
        '<section class="ve-hero">'
        f'<p class="ve-eyebrow">{escape(eyebrow)}</p>'
        f'<h1 class="ve-title">{escape(title)}</h1>'
        f'<p class="ve-lede">{escape(subtitle)}</p>'
        f"{foot}"
        "</section>"
    )


def stats_html(items: list[tuple[str, str]]) -> str:
    cells = "".join(
        '<div class="ve-stat">'
        f'<span class="ve-stat-v">{escape(value)}</span>'
        f'<span class="ve-stat-l">{escape(label)}</span>'
        "</div>"
        for value, label in items
    )
    return f'<div class="ve-stats">{cells}</div>'


def cards_html(items: list[tuple[str, str, str]]) -> str:
    """``items`` is ``(title, chip, description)`` per card."""
    cards = "".join(
        '<article class="ve-card">'
        f'<span class="ve-chip">{escape(chip)}</span>'
        f"<h3>{escape(title)}</h3>"
        f"<p>{escape(desc)}</p>"
        "</article>"
        for title, chip, desc in items
    )
    return f'<div class="ve-grid">{cards}</div>'


def badge_html() -> str:
    """The badge that keeps the demo honest: mock or live, never implied."""
    if config.is_mock_mode():
        return (
            '<span class="ve-badge ve-badge--mock">'
            '<span class="ve-dot"></span>Mock mode · no API key</span>'
        )
    return (
        '<span class="ve-badge ve-badge--live">'
        '<span class="ve-dot"></span>Live · Sarvam AI</span>'
    )


def panel_html(text: str) -> str:
    return f'<div class="ve-panel"><p>{escape(text)}</p></div>'


# ---------------------------------------------------------------- render


def _render(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def inject_css() -> None:
    """Load assets/styles.css once per rerun."""
    css_path = config.ASSETS_DIR / "styles.css"
    if not css_path.exists():  # pragma: no cover - guards a broken checkout
        return
    _render(f"<style>{css_path.read_text(encoding='utf-8')}</style>")


def aurora() -> None:
    _render(aurora_html())


def hero(eyebrow: str, title: str, subtitle: str, pills: list[str] | None = None) -> None:
    _render(hero_html(eyebrow, title, subtitle, pills))


def stat_strip(items: list[tuple[str, str]]) -> None:
    _render(stats_html(items))


def tilt_cards(items: list[tuple[str, str, str]]) -> None:
    _render(cards_html(items))


def provider_badge() -> None:
    _render(badge_html())


def panel(text: str) -> None:
    _render(panel_html(text))


def note(text: str) -> None:
    _render(f'<p class="ve-note">{escape(text)}</p>')


def section_label(text: str) -> None:
    _render(f'<p class="ve-section">{escape(text)}</p>')


def enhance_js() -> None:
    """Optional pointer tilt and parallax, in a zero-height same-origin frame.

    If it never runs, the CSS hover tilt and entrance animations still work —
    nothing on the page depends on this succeeding.
    """
    js_path = config.ASSETS_DIR / "app.js"
    if not js_path.exists():  # pragma: no cover
        return
    js = js_path.read_text(encoding="utf-8")
    # st.iframe embeds an HTML string as a same-origin frame with JS enabled,
    # which is what lets the enhancer reach window.parent.document.
    st.iframe(
        src=f"<!doctype html><html><body><script>{js}</script></body></html>",
        height=1,
        width=1,
    )
