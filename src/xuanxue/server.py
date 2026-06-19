"""MCP 服务层 — 命理分析 HTTP API"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from xuanxue.core.dispatcher import resolve_methods, select_for_full_reading
from xuanxue.core.registry import registry, MethodStatus, MethodResult
from xuanxue.core.synthesis import SynthesisEngine
from xuanxue.analyzers.dimension_extractor import extract_dimensions
from xuanxue.export.report import build_report, to_json, to_markdown

# 确保方法已注册
import xuanxue.core.methods  # noqa: F401

app = FastAPI(
    title="综合玄学命理分析",
    description="融合八字、紫微、奇门、称骨的多技法交叉命理分析服务",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 请求/响应模型 ──────────────────────────────────────────────


class AnalyzeRequest(BaseModel):
    """分析请求"""
    name: str = Field(default="命主", description="姓名")
    gender: str = Field(description="性别：male/female")
    birth_datetime: str = Field(description="出生时间，如 1990-05-15 15:00")
    calendar_type: str = Field(default="solar", description="历法：solar/lunar")
    birthplace: str = Field(default="", description="出生地")
    timezone: str = Field(default="Asia/Shanghai", description="时区")
    methods: list[str] | None = Field(default=None, description="指定方法列表，None=自动选择")
    focus: str | None = Field(default=None, description="关注重点：career/wealth/relationship/health")


class MethodStatusInfo(BaseModel):
    """方法状态"""
    name: str
    display_name: str
    status: str
    confidence: float | None = None


class AnalyzeResponse(BaseModel):
    """分析响应"""
    name: str
    birth_info: dict[str, Any]
    methods_used: list[MethodStatusInfo]
    report_markdown: str
    report_json: str


# ── API 端点 ──────────────────────────────────────────────────


@app.get("/health")
async def health() -> dict[str, str]:
    """健康检查"""
    return {"status": "ok", "version": "0.1.0"}


@app.get("/methods")
async def list_methods() -> list[dict[str, Any]]:
    """列出所有可用方法"""
    return [
        {
            "name": entry.name,
            "display_name": entry.display_name,
            "description": entry.description,
            "required_fields": ", ".join(entry.required_fields),
        }
        for entry in registry.list_all()
    ]


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    """综合命理分析"""
    input_data: dict[str, Any] = {
        "name": req.name,
        "gender": req.gender,
        "birth_datetime": req.birth_datetime,
        "calendar_type": req.calendar_type,
        "birthplace": req.birthplace,
        "timezone": req.timezone,
    }

    # 1. 运行各方法
    if req.methods:
        # 指定方法
        results: list[MethodResult] = []
        for method_name in req.methods:
            result = registry.run_method(method_name, input_data)
            results.append(result)
    else:
        # 自动选择所有可运行方法
        results = resolve_methods("综合分析", registry, input_data)

    # 2. 提取维度信号并注入到结果
    enriched: list[MethodResult] = []
    for r in results:
        if r.status == MethodStatus.RUNNABLE and r.facts:
            dims = extract_dimensions(r.method, r.facts)
            enriched_facts = {**r.facts, **dims}
            enriched.append(MethodResult(
                method=r.method, status=r.status, facts=enriched_facts,
                interpretation=r.interpretation, confidence=r.confidence,
                blockers=r.blockers, evidence=r.evidence,
            ))
        else:
            enriched.append(r)

    # 3. 交叉验证综合
    synthesis_engine = SynthesisEngine()
    synthesis = synthesis_engine.synthesize(enriched)

    # 4. 构建报告
    method_results = {}
    for r in enriched:
        if r.status == MethodStatus.RUNNABLE and r.facts:
            method_results[r.method] = r.facts

    report = build_report(
        name=req.name,
        birth_info=input_data,
        method_results=method_results,
        synthesis={
            "final_verdict": synthesis.final_verdict,
            "runnable_methods": synthesis.runnable_methods,
            "blocked_methods": synthesis.blocked_methods,
            "dimension_verdicts": [
                {
                    "dimension": v.dimension,
                    "best_method": v.best_method,
                    "confidence": v.confidence,
                    "consensus": v.consensus,
                }
                for v in synthesis.dimensions
            ],
        },
    )

    methods_used = [
        MethodStatusInfo(
            name=r.method,
            display_name=registry.get(r.method).display_name if registry.get(r.method) else r.method,
            status=r.status.value,
            confidence=None,
        )
        for r in results
    ]

    return AnalyzeResponse(
        name=req.name,
        birth_info=input_data,
        methods_used=methods_used,
        report_markdown=to_markdown(report),
        report_json=to_json(report),
    )


@app.post("/calculate/{method}")
async def calculate_single(method: str, req: AnalyzeRequest) -> dict[str, Any]:
    """单方法排盘计算"""
    entry = registry.get(method)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"未知方法: {method}")

    input_data: dict[str, Any] = {
        "name": req.name,
        "gender": req.gender,
        "birth_datetime": req.birth_datetime,
        "calendar_type": req.calendar_type,
        "birthplace": req.birthplace,
        "timezone": req.timezone,
    }

    status = registry.check_status(method, input_data)
    if status != MethodStatus.RUNNABLE:
        raise HTTPException(status_code=400, detail=f"方法 {method} 不可运行: {status.value}")

    result = registry.run_method(method, input_data)
    return {
        "method": method,
        "display_name": entry.display_name,
        "status": status.value,
        "facts": result.facts,
    }


# ── CLI 入口 ──────────────────────────────────────────────────


def main() -> None:
    """启动服务"""
    import uvicorn

    host = "0.0.0.0"
    port = 8600
    print(f"🔮 玄学命理分析服务启动中: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
