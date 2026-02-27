# Embedded Engineer Agent MVP Demo

一个最小可运行 Demo，演示“知识库 + 内嵌工程师 Agent（排障模式）”。

## 能力范围（MVP）
- 知识库 MVP：内置 `data/knowledge_items.json`，包含 SOP / Case 示例。
- 知识检索：`POST /knowledge/search`，支持基础过滤与关键词匹配。
- 排障 Agent：`POST /agent/troubleshoot`，输出结构化排障建议（原因、依据、步骤、风险）。

## 快速运行
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

访问：`http://127.0.0.1:8000/docs`

## 示例请求
```bash
curl -X POST http://127.0.0.1:8000/agent/troubleshoot \
  -H 'Content-Type: application/json' \
  -d '{"query":"gateway 502 and upstream failed", "instance_id":"ins_001"}'
```

## 测试
```bash
pytest -q
```
