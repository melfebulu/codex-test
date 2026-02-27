from __future__ import annotations

from .kb import KnowledgeBase
from .models import SearchRequest, TroubleshootRequest, TroubleshootResponse


class TroubleshootAgent:
    def __init__(self, kb: KnowledgeBase) -> None:
        self.kb = kb

    def run(self, req: TroubleshootRequest) -> TroubleshootResponse:
        module = self._guess_module(req.query)
        search_result = self.kb.search(
            SearchRequest(
                query=req.query,
                scene_type="troubleshooting",
                module=module,
                deployment_mode=req.context.get("deployment_mode"),
                version=req.context.get("version"),
                top_k=3,
            )
        )

        evidence = [
            {
                "id": f"e{idx + 1}",
                "type": "knowledge",
                "title": item.title,
                "snippet": item.content[:120],
                "source_id": item.knowledge_id,
            }
            for idx, item in enumerate(search_result)
        ]

        if not search_result:
            return TroubleshootResponse(
                summary="当前知识库命中不足，先给出通用排障建议。",
                possible_causes=[{"id": "c1", "title": "信息不足，无法定位具体根因", "confidence": 0.2, "evidence_refs": []}],
                evidence=[],
                steps=[
                    {"seq": 1, "title": "补充关键错误日志", "detail": "请提供 1~3 行包含 ERROR/Exception 的日志", "priority": "P1", "risk_level": "low"},
                    {"seq": 2, "title": "提供部署模式和版本", "detail": "补充 instance_id 或版本信息提升命中率", "priority": "P1", "risk_level": "low"},
                ],
                risk_tips=["当前建议为通用模板，不建议直接执行高风险变更。"],
                applicability={"version_range": "通用", "deployment_modes": ["all"], "modules": ["all"]},
                need_more_info=["关键日志", "版本", "部署模式"],
                next_actions=["补充信息后重试分析"],
                degrade_notice="知识库命中不足，已降级为通用排障建议。",
            )

        top = search_result[0]
        causes = [
            {"id": "c1", "title": f"{top.module} 模块的常见配置或连通性异常", "confidence": 0.78, "evidence_refs": ["e1"]},
            {"id": "c2", "title": "依赖组件未就绪或健康状态异常", "confidence": 0.62, "evidence_refs": ["e1"]},
        ]
        steps = [
            {"seq": 1, "title": "核对配置项与目标环境", "detail": "优先检查连接地址、端口、认证参数是否匹配。", "priority": "P1", "risk_level": "low"},
            {"seq": 2, "title": "验证依赖组件健康状态", "detail": "确认数据库/缓存/消息队列可达且状态正常。", "priority": "P1", "risk_level": "low"},
            {"seq": 3, "title": "按 SOP 执行分步排查", "detail": f"参考知识条目 {top.knowledge_id} 的步骤执行。", "priority": "P2", "risk_level": "low"},
        ]

        return TroubleshootResponse(
            summary=f"已结合知识库给出排障建议，优先关注 {top.module} 模块。",
            possible_causes=causes,
            evidence=evidence,
            steps=steps,
            risk_tips=["执行变更前请保留配置快照。", "未确认根因前避免频繁重启服务。"],
            applicability={
                "version_range": f"{top.version_min}-{top.version_max}",
                "deployment_modes": top.deployment_modes,
                "modules": [top.module],
            },
            need_more_info=[] if req.instance_id else ["建议提供 instance_id 以绑定实例上下文"],
            next_actions=["完成 P1 检查项后反馈结果，继续下一轮分析。"],
            degrade_notice=None,
        )

    @staticmethod
    def _guess_module(query: str) -> str | None:
        q = query.lower()
        for key in ["gateway", "app", "db", "database", "redis", "mq"]:
            if key in q:
                return "db" if key == "database" else key
        return None
