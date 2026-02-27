from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class KnowledgeItem(BaseModel):
    knowledge_id: str
    title: str
    knowledge_type: Literal["sop", "case", "config", "release", "manual"]
    scene_type: Literal["troubleshooting", "deploy", "upgrade", "inspect"]
    module: str
    version_min: str
    version_max: str
    deployment_modes: list[str]
    tags: list[str] = Field(default_factory=list)
    content: str


class SearchRequest(BaseModel):
    query: str
    scene_type: Literal["troubleshooting", "deploy", "upgrade", "inspect"] = "troubleshooting"
    module: str | None = None
    version: str | None = None
    deployment_mode: str | None = None
    top_k: int = 5


class TroubleshootRequest(BaseModel):
    query: str
    instance_id: str | None = None
    session_id: str | None = None
    attachments: list[dict] = Field(default_factory=list)
    context: dict = Field(default_factory=dict)


class TroubleshootResponse(BaseModel):
    summary: str
    possible_causes: list[dict]
    evidence: list[dict]
    steps: list[dict]
    risk_tips: list[str]
    applicability: dict
    need_more_info: list[str]
    next_actions: list[str]
    degrade_notice: str | None = None
