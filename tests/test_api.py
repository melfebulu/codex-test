from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_knowledge_search() -> None:
    r = client.post(
        "/knowledge/search",
        json={"query": "gateway 502 upstream", "scene_type": "troubleshooting", "top_k": 2},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["count"] >= 1


def test_troubleshoot_response_structure() -> None:
    r = client.post(
        "/agent/troubleshoot",
        json={"query": "gateway 502 and upstream failed", "instance_id": "ins_1"},
    )
    assert r.status_code == 200
    result = r.json()["result"]
    for key in ["summary", "possible_causes", "evidence", "steps", "risk_tips", "next_actions"]:
        assert key in result
    assert result["degrade_notice"] is None
