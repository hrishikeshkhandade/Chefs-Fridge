"""Checks how the app talks to Gemini: which photos it sends, what it remembers, and what it does when the model fails.

Run:  uv run --with-requirements requirements.txt --with pytest pytest -q
No API key or network is needed: the Gemini client is replaced by a stand-in.
"""
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


class FakeClient:
    """Stands in for google.genai.Client. Answers a photo with whatever food was registered for it."""

    def __init__(self):
        self.models = self
        self.answers = {}
        self.requests = []
        self.fail = False
        self.text = "Tomato Soup\n\nINGREDIENTS:\ntomatoes\n\nINSTRUCTIONS:\n1. Simmer."

    def sees(self, image, text):
        self.answers[app.image_to_bytes(image)] = text

    def generate_content(self, *, model, contents, config=None):
        self.requests.append({"model": model, "contents": contents, "config": config})
        if self.fail:
            raise RuntimeError("model is down")
        if isinstance(contents, str):
            return type("Response", (), {"text": self.text})()
        part = contents[1]
        assert part.inline_data.mime_type == "image/jpeg"
        return type("Response", (), {"text": self.answers[part.inline_data.data]})()


@pytest.fixture
def client(monkeypatch):
    fake = FakeClient()
    monkeypatch.setattr(app, "client", fake)
    app.identify_items.clear()
    return fake


def test_different_photos_give_different_ingredients(client):
    fridge, pantry = photo("red"), photo("blue")
    client.sees(fridge, "eggs, milk")
    client.sees(pantry, "rice, lentils")

    assert sorted(app.identify_items([fridge])) == ["eggs", "milk"]
    assert sorted(app.identify_items([pantry])) == ["lentils", "rice"]


def test_the_same_photos_are_only_sent_once(client):
    fridge = photo("green")
    client.sees(fridge, "spinach, tofu")

    first = app.identify_items([fridge])
    second = app.identify_items([photo("green")])

    assert sorted(first) == sorted(second) == ["spinach", "tofu"]
    assert len(client.requests) == 1


def test_a_failed_request_is_not_remembered(client):
    fridge = photo("yellow")
    client.sees(fridge, "butter, cheese")

    client.fail = True
    assert app.identify_items([fridge]) == []

    client.fail = False
    assert sorted(app.identify_items([fridge])) == ["butter", "cheese"]


def test_an_empty_answer_is_an_error_not_an_empty_fridge(client):
    fridge = photo("white")
    client.sees(fridge, None)
    assert app.identify_items([fridge]) == []

    client.sees(fridge, "yogurt")
    assert app.identify_items([fridge]) == ["yogurt"]


def test_every_request_names_the_configured_model(client):
    fridge = photo("orange")
    client.sees(fridge, "carrots")
    app.identify_items([fridge])
    app.generate_recipe(["carrots"], "None", "Any")

    assert [r["model"] for r in client.requests] == [app.GEMINI_MODEL, app.GEMINI_MODEL]
    assert app.GEMINI_MODEL == os.getenv("GEMINI_MODEL", app.DEFAULT_GEMINI_MODEL)
    assert "2.0" not in app.DEFAULT_GEMINI_MODEL


def test_a_recipe_request_carries_the_ingredients_and_preferences(client):
    client.text = "**Veggie Tacos**\n\nINGREDIENTS:\n* beans\n\nINSTRUCTIONS:\n1. Warm the beans."

    recipe = app.generate_recipe(["beans", "tortillas"], "Vegan", "Mexican")

    prompt = client.requests[-1]["contents"]
    assert "beans, tortillas" in prompt
    assert "vegan" in prompt and "Mexican cuisine" in prompt
    assert recipe.startswith("Veggie Tacos")
    assert "*" not in recipe


def test_a_failed_recipe_request_says_so(client):
    client.fail = True
    assert app.generate_recipe(["beans"], "None", "Any") == "Unable to generate recipe."
    client.fail = False
    client.text = None
    assert app.generate_recipe(["beans"], "None", "Any") == "Unable to generate recipe."
