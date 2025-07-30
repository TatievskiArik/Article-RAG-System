import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

client = TestClient(app)

def test_healthcheck():
    response = client.get("/")
    assert response.status_code == 200

def test_articles_list(monkeypatch):
    response = client.get("/articles/list")
    assert response.status_code == 200
    data = response.json()
    assert "articles" in data
    assert isinstance(data["articles"], list)
    # Ensure all items have the correct structure
    for item in data["articles"]:
        assert isinstance(item, dict)
        assert set(item.keys()) == {"title", "url"}
        assert isinstance(item["title"], str)
        assert isinstance(item["url"], str)

def test_add_article_already_exists():
    response = client.post("/articles/add", json={"url": "https://techcrunch.com/2025/07/11/ai-coding-tools-may-not-speed-up-every-developer-study-shows/"})
    assert response.status_code == 208
    assert response.json()["message"] == "Article already exists."
