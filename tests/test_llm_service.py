import asyncio

from app.services import llm_service


def test_classify_aisle_uses_local_fallback_when_gemini_fails(monkeypatch):

    def raise_unavailable(*args, **kwargs):
        raise RuntimeError("503 UNAVAILABLE")

    monkeypatch.setattr(
        llm_service.client.models,
        "generate_content",
        raise_unavailable,
    )

    aisle = asyncio.run(
        llm_service.classify_aisle("yogurt")
    )

    assert aisle == "dairy"


def test_classify_aisle_uses_local_fallback_for_invalid_gemini_response(monkeypatch):

    class Response:
        text = "not-an-aisle"

    monkeypatch.setattr(
        llm_service.client.models,
        "generate_content",
        lambda *args, **kwargs: Response(),
    )

    aisle = asyncio.run(
        llm_service.classify_aisle("sourdough bread")
    )

    assert aisle == "bakery"


def test_classify_aisle_rejects_not_grocery_response(monkeypatch):

    class Response:
        text = "not_grocery"

    monkeypatch.setattr(
        llm_service.client.models,
        "generate_content",
        lambda *args, **kwargs: Response(),
    )

    try:
        asyncio.run(
            llm_service.classify_aisle("sidhant")
        )
    except llm_service.NonGroceryItemError as exc:
        assert str(exc) == "Item is not a grocery item."
    else:
        raise AssertionError(
            "Expected NonGroceryItemError"
        )


def test_classify_aisle_rejects_unknown_item_when_gemini_fails(monkeypatch):

    def raise_unavailable(*args, **kwargs):
        raise RuntimeError("503 UNAVAILABLE")

    monkeypatch.setattr(
        llm_service.client.models,
        "generate_content",
        raise_unavailable,
    )

    try:
        asyncio.run(
            llm_service.classify_aisle("sidhant")
        )
    except llm_service.NonGroceryItemError as exc:
        assert str(exc) == "Item is not a grocery item."
    else:
        raise AssertionError(
            "Expected NonGroceryItemError"
        )
