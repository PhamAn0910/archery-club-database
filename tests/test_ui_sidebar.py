import pytest

from ui_sidebar import _profile_card_html, _visible_sections, AuthState


def test_profile_card_html_empty():
    auth = AuthState(logged_in=True, name=None, av=None)
    html = _profile_card_html(auth)
    assert "Logged in as" in html
    assert "profile-card" in html


def test_visible_sections_defaults():
    auth = AuthState()
    sections = _visible_sections(auth)
    assert "Home" in sections
    assert "Public" in sections


def test_visible_sections_archer():
    auth = AuthState(logged_in=True, is_recorder=False)
    sections = _visible_sections(auth)
    assert "Archer" in sections


def test_visible_sections_recorder():
    auth = AuthState(logged_in=True, is_recorder=True)
    sections = _visible_sections(auth)
    assert "Recorder" in sections
