"""Append-only event log — the analytics source of truth.

One helper, ``log_event()``, called on the same line as the user action that
produced it. Nothing in the app updates or deletes from ``events``; that is
what makes the Power BI numbers trustworthy.

Logging never raises: a failed insert is printed to stderr and the lesson
keeps running. Learning must not stop because a write failed.
"""

from __future__ import annotations

import json
import sys
import uuid
from typing import Any

from core import db

try:  # Streamlit is optional so services and tests can import this module.
    import streamlit as st
except ModuleNotFoundError:  # pragma: no cover - streamlit is in requirements
    st = None  # type: ignore[assignment]


# Documented event names. Adding one is fine; renaming one breaks the report.
EVENT_NAMES: frozenset[str] = frozenset(
    {
        "app_opened",
        "page_viewed",
        "ui_language_changed",
        "translation_requested",
        "translation_copied",
        "term_glossed",
        "word_saved",
        "lesson_opened",
        "segment_read",
        "lesson_completed",
        "quiz_started",
        "quiz_submitted",
        "quiz_passed",
        "tutor_question_asked",
        "tutor_refused_ungrounded",
        "recommendation_shown",
        "export_refreshed",
    }
)


def new_session_id() -> str:
    return uuid.uuid4().hex[:16]


def _session_value(key: str, default: Any = None) -> Any:
    if st is None:
        return default
    try:
        return st.session_state.get(key, default)
    except Exception:  # no session context (bare pytest, script import)
        return default


def ensure_session(ui_language: str | None = None) -> None:
    """Bootstrap session id and local user. Called once per browser session."""
    if st is None:  # pragma: no cover
        return
    if not st.session_state.get("session_id"):
        st.session_state["session_id"] = new_session_id()
    if not st.session_state.get("user_id"):
        st.session_state["user_id"] = db.ensure_local_user(
            ui_language or st.session_state.get("ui_language", "en-IN")
        )


def log_event(
    event_name: str,
    *,
    user_id: int | None = None,
    lang: str | None = None,
    session_id: str | None = None,
    **props: Any,
) -> None:
    """Append one event. Extra keyword arguments become the JSON ``props``."""
    resolved_user = user_id if user_id is not None else _session_value("user_id")
    resolved_lang = lang if lang is not None else _session_value("ui_language")
    resolved_session = (
        session_id if session_id is not None else _session_value("session_id")
    )
    try:
        with db.get_conn() as conn:
            conn.execute(
                "INSERT INTO events (user_id, event_name, props, lang, session_id)"
                " VALUES (?, ?, ?, ?, ?)",
                (
                    resolved_user,
                    event_name,
                    json.dumps(props, ensure_ascii=False) if props else None,
                    resolved_lang,
                    resolved_session,
                ),
            )
    except Exception as exc:  # pragma: no cover - defensive by design
        print(f"[events] failed to log {event_name}: {exc}", file=sys.stderr)


def recent_events(limit: int = 5) -> list[dict[str, Any]]:
    """Newest events first — used by the Home page's proof panel."""
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT event_name, props, lang, created_at FROM events"
            " ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def event_counts() -> dict[str, int]:
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT event_name, COUNT(*) AS n FROM events GROUP BY event_name"
            " ORDER BY n DESC"
        ).fetchall()
    return {row["event_name"]: int(row["n"]) for row in rows}
