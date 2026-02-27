from __future__ import annotations

from fastapi import FastAPI

from .agent import TroubleshootAgent
from .kb import KnowledgeBase
from .models import SearchRequest, TroubleshootRequest

app = FastAPI(title="Embedded Engineer Agent MVP", version="0.1.0")
kb = KnowledgeBase()
agent = TroubleshootAgent(kb)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/knowledge/items")
def knowledge_items() -> list[dict]:
    return [i.model_dump() for i in kb.items]


@app.post("/knowledge/search")
def knowledge_search(req: SearchRequest) -> dict:
    items = kb.search(req)
    return {"count": len(items), "items": [i.model_dump() for i in items]}


@app.post("/agent/troubleshoot")
def troubleshoot(req: TroubleshootRequest) -> dict:
    result = agent.run(req)
    return {"mode": "troubleshooting", "result": result.model_dump()}
