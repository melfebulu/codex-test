from __future__ import annotations

import json
from pathlib import Path

from .models import KnowledgeItem, SearchRequest


class KnowledgeBase:
    def __init__(self, data_file: str = "data/knowledge_items.json") -> None:
        self.data_file = Path(data_file)
        self.items: list[KnowledgeItem] = []
        self.load()

    def load(self) -> None:
        data = json.loads(self.data_file.read_text(encoding="utf-8"))
        self.items = [KnowledgeItem(**item) for item in data]

    def search(self, req: SearchRequest) -> list[KnowledgeItem]:
        query_tokens = self._tokenize(req.query)

        filtered = [
            i
            for i in self.items
            if i.scene_type == req.scene_type
            and (req.module is None or i.module == req.module)
            and (
                req.deployment_mode is None
                or req.deployment_mode in i.deployment_modes
                or "all" in i.deployment_modes
            )
        ]

        scored: list[tuple[int, KnowledgeItem]] = []
        for item in filtered:
            haystack = self._tokenize(" ".join([item.title, item.content, " ".join(item.tags)]))
            score = len(set(query_tokens) & set(haystack))
            if score > 0:
                scored.append((score, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[: req.top_k]]

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return [tok.strip().lower() for tok in text.replace("\n", " ").replace("/", " ").split() if tok.strip()]
