from fastapi.testclient import TestClient

from app.services import llm_service

from app.main import app

client = TestClient(app)


def test_health():

    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy"
    }


def test_measured_rule():

    response = client.post(
        "/api/classify",
        json={
            "item": "2 kg rice"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["tag_type"] == "measured"


def test_staple_rule():

    response = client.post(
        "/api/classify",
        json={
            "item": "salt"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["tag_type"] == "staple"


def test_non_grocery_item_returns_validation_error(monkeypatch):

    class Response:
        text = "not_grocery"

    monkeypatch.setattr(
        llm_service.client.models,
        "generate_content",
        lambda *args, **kwargs: Response(),
    )

    response = client.post(
        "/api/classify",
        json={
            "item": "sidhant"
        },
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": "Item is not a grocery item."
    }
