"""Boots the real app.py headlessly and asserts the shell renders in two languages.

This is the test that would have caught a broken import, a bad navigation path
or a CSS file that went missing — the failures that only show up at runtime.
"""

from __future__ import annotations

from streamlit.testing.v1 import AppTest


def _boot(tmp_path, monkeypatch) -> AppTest:
    monkeypatch.setenv("VE_DB_PATH", str(tmp_path / "app.db"))
    monkeypatch.delenv("SARVAM_API_KEY", raising=False)
    app = AppTest.from_file("../app.py", default_timeout=90)
    return app.run()


def test_app_boots_in_mock_mode(tmp_path, monkeypatch):
    at = _boot(tmp_path, monkeypatch)
    assert not at.exception, [e.value for e in at.exception]
    assert len(at.sidebar.selectbox) == 1
    assert at.sidebar.selectbox[0].value == "en-IN"


def test_switching_language_changes_the_page(tmp_path, monkeypatch):
    at = _boot(tmp_path, monkeypatch)
    at.sidebar.selectbox[0].select("te-IN").run()
    assert not at.exception, [e.value for e in at.exception]
    rendered = " ".join(block.value for block in at.markdown)
    assert "నేర్చుకోండి" in rendered  # Telugu tagline is actually on screen


def test_translate_page_produces_a_mock_translation(tmp_path, monkeypatch):
    at = _boot(tmp_path, monkeypatch)
    at.switch_page("pages/2_Translate.py").run()
    assert not at.exception, [e.value for e in at.exception]
    assert [b.label for b in at.button] == ["Try an example", "Translate"]

    at.text_area[0].set_value("plant water food").run()
    at.button[1].click().run()

    assert not at.exception, [e.value for e in at.exception]
    assert at.code[0].value == "पौधा पानी भोजन", "mock dictionary path is wired end to end"


def test_learn_page_scores_the_quiz_and_records_it(tmp_path, monkeypatch):
    at = _boot(tmp_path, monkeypatch)
    at.switch_page("pages/3_Learn.py").run()
    assert not at.exception, [e.value for e in at.exception]
    assert len(at.radio) == 3

    for radio in at.radio:
        radio.set_value(0)
    at.run()

    labels = [button.label for button in at.button]
    at.button[labels.index("Check answers")].click().run()

    assert not at.exception, [e.value for e in at.exception]
    assert at.metric[0].value == "3/3"
    assert at.metric[1].value == "100%"


def test_learn_page_glosses_a_term_in_the_reading_language(tmp_path, monkeypatch):
    at = _boot(tmp_path, monkeypatch)
    at.sidebar.selectbox[0].select("te-IN").run()
    at.switch_page("pages/3_Learn.py").run()

    at.button[0].click().run()
    assert not at.exception, [e.value for e in at.exception]

    entry = at.session_state["gloss"]
    assert entry["term"] == "fraction"
    assert entry["authored"] == "translated", "Telugu gloss is filled by the service"


def test_tutor_answers_then_refuses(tmp_path, monkeypatch):
    at = _boot(tmp_path, monkeypatch)
    at.switch_page("pages/4_Tutor.py").run()
    assert not at.exception, [e.value for e in at.exception]

    # the tutor is grounded in the selected lesson, so pick the photosynthesis one
    at.selectbox[0].set_value("science-photosynthesis-01").run()
    at.chat_input[0].set_value("What do plants need to make food?").run()
    assert not at.exception, [e.value for e in at.exception]
    grounded = " ".join(block.value for block in at.markdown)
    assert "From the lesson" in grounded or "पाठ से" in grounded

    at.chat_input[0].set_value("Who won the cricket world cup?").run()
    assert not at.exception, [e.value for e in at.exception]
    refused = " ".join(block.value for block in at.markdown)
    assert "not covered" in refused or "नहीं है" in refused


def test_progress_recommends_a_real_lesson(tmp_path, monkeypatch):
    at = _boot(tmp_path, monkeypatch)
    at.switch_page("pages/5_Progress.py").run()
    assert not at.exception, [e.value for e in at.exception]

    body = " ".join(block.value for block in at.markdown)
    assert "You have not opened" in body, "rule-based reason is rendered"
    assert at.metric[3].label == "Events logged"


def test_analytics_page_exports_the_csvs(tmp_path, monkeypatch):
    monkeypatch.setenv("VE_EXPORT_DIR", str(tmp_path / "exports"))
    at = _boot(tmp_path, monkeypatch)
    at.switch_page("pages/6_Analytics.py").run()
    assert not at.exception, [e.value for e in at.exception]

    labels = [button.label for button in at.button]
    at.button[labels.index("Refresh export")].click().run()

    assert not at.exception, [e.value for e in at.exception]
    written = sorted(p.name for p in (tmp_path / "exports").iterdir())
    assert written == [
        "_health.json",
        "dim_lessons.csv",
        "dim_users.csv",
        "fact_events.csv",
        "fact_translations.csv",
    ]
