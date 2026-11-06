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
