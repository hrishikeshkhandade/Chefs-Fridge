"""Checks that ingredient detection answers for the photos it was given.

Run:  uv run --with-requirements requirements.txt --with pytest pytest -q
No API key or network is needed: the model is replaced by a stand-in.
"""
import base64
import os
import sys
from pathlib import Path

import pytest
from PIL import Image

os.environ.setdefault("GEMINI_API_KEY", "test-key")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import app  # noqa: E402


def photo(color):
    return Image.new("RGB", (32, 32), color)


class FakeModel:
    """Answers with whatever food was registered for the exact image it is sent."""

    def __init__(self):
        self.answers = {}
        self.calls = 0
        self.fail = False

    def sees(self, image, text):
        self.answers[base64.b64encode(app.image_to_bytes(image)).decode("utf-8")] = text

    def generate_content(self, parts):
        self.calls += 1
        if self.fail:
            raise RuntimeError("model is down")
        return type("Response", (), {"text": self.answers[parts[1]["data"]]})()


@pytest.fixture
def model(monkeypatch):
    fake = FakeModel()
    monkeypatch.setattr(app, "model", fake)
    app.identify_items.clear()
    return fake


def test_different_photos_give_different_ingredients(model):
    fridge, pantry = photo("red"), photo("blue")
    model.sees(fridge, "eggs, milk")
    model.sees(pantry, "rice, lentils")

    assert sorted(app.identify_items([fridge])) == ["eggs", "milk"]
    assert sorted(app.identify_items([pantry])) == ["lentils", "rice"]


def test_the_same_photos_are_only_sent_once(model):
    fridge = photo("green")
    model.sees(fridge, "spinach, tofu")

    first = app.identify_items([fridge])
    second = app.identify_items([photo("green")])

    assert sorted(first) == sorted(second) == ["spinach", "tofu"]
    assert model.calls == 1


def test_a_failed_request_is_not_remembered(model):
    fridge = photo("yellow")
    model.sees(fridge, "butter, cheese")

    model.fail = True
    assert app.identify_items([fridge]) == []

    model.fail = False
    assert sorted(app.identify_items([fridge])) == ["butter", "cheese"]
