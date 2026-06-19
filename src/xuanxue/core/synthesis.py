"""综合分析引擎 — 多技法交叉验证 + 六维度归一化输出"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from xuanxue.core.registry import MethodResult, MethodStatus

DIMENSIONS = ["personality", "career", "wealth", "relationship", "health", "timing"]

DIMENSION_LABELS: dict[str, str] = {
    "personality": "性格", "career": "事业", "wealth": "财运",
    "relationship": "关系", "health": "身心", "timing": "阶段运势",
}

METHOD_DISPLAY: dict[str, str] = {
    "bazi": "八字", "ziwei": "紫微斗数", "qimen": "奇门遁甲", "chenggu": "称骨",
}

METHOD_WEIGHTS: dict[str, dict[str, float]] = {
    "bazi":        {"personality": 0.9, "career": 0.8, "wealth": 0.8, "relationship": 0.7, "health": 0.6, "timing": 0.9},
    "ziwei":       {"personality": 0.9, "career": 0.9, "wealth": 0.8, "relationship": 0.9, "health": 0.7, "timing": 0.8},
    "qimen":       {"personality": 0.3, "career": 0.7, "wealth": 0.5, "relationship": 0.3, "health": 0.2, "timing": 0.8},
    "chenggu":     {"personality": 0.5, "career": 0.5, "wealth": 0.5, "relationship": 0.4, "health": 0.3, "timing": 0.6},
    "numerology":  {"personality": 0.7, "career": 0.6, "wealth": 0.6, "relationship": 0.5, "health": 0.3, "timing": 0.4},
    "meihua":      {"personality": 0.4, "career": 0.6, "wealth": 0.5, "relationship": 0.4, "health": 0.3, "timing": 0.7},
    "liuyao":      {"personality": 0.4, "career": 0.6, "wealth": 0.5, "relationship": 0.4, "health": 0.3, "timing": 0.7},
    "liuren":      {"personality": 0.3, "career": 0.6, "wealth": 0.5, "relationship": 0.3, "health": 0.2, "timing": 0.8},
    "jinkou":      {"personality": 0.3, "career": 0.5, "wealth": 0.4, "relationship": 0.3, "health": 0.2, "timing": 0.7},
    "western":     {"personality": 0.7, "career": 0.5, "wealth": 0.4, "relationship": 0.6, "health": 0.4, "timing": 0.5},
    "vedic":       {"personality": 0.6, "career": 0.5, "wealth": 0.4, "relationship": 0.5, "health": 0.4, "timing": 0.6},
}


@dataclass(frozen=True)
class DimensionVerdict:
    dimension: str
    method_signals: dict[str, str] = field(default_factory=dict)
    consensus: str = ""
    confidence: str = "medium"
    conflicts: list[str] = field(default_factory=list)
    best_method: str = ""


@dataclass(frozen=True)
class SynthesisOutput:
    runnable_methods: list[str] = field(default_factory=list)
    blocked_methods: list[str] = field(default_factory=list)
    dimensions: list[DimensionVerdict] = field(default_factory=list)
    final_verdict: str = ""


class SynthesisEngine:
    def __init__(self, min_agreement: int = 2) -> None:
        self._min_agreement = min_agreement

    def synthesize(self, results: list[MethodResult]) -> SynthesisOutput:
        runnable = [r for r in results if r.status != MethodStatus.BLOCKED]
        blocked = [r for r in results if r.status == MethodStatus.BLOCKED]

        if not runnable:
            return SynthesisOutput(
                blocked_methods=[r.method for r in blocked],
                final_verdict="所有方法均无法运行，请补充信息后重试。",
            )

        dim_signals: dict[str, dict[str, str]] = {d: {} for d in DIMENSIONS}
        for result in runnable:
            for dim in DIMENSIONS:
                signal = result.facts.get(dim, "")
                if signal:
                    dim_signals[dim][result.method] = signal

        verdicts = [self._resolve(d, s) for d, s in dim_signals.items()]
        final = self._generate_final(verdicts, runnable)

        return SynthesisOutput(
            runnable_methods=[r.method for r in runnable],
            blocked_methods=[r.method for r in blocked],
            dimensions=verdicts,
            final_verdict=final,
        )

    def _resolve(self, dim: str, signals: dict[str, str]) -> DimensionVerdict:
        if not signals:
            return DimensionVerdict(dimension=dim, confidence="low")

        unique = list(set(s.strip() for s in signals.values() if s.strip()))
        best = max(signals.keys(), key=lambda m: METHOD_WEIGHTS.get(m, {}).get(dim, 0))

        if len(unique) <= 1:
            return DimensionVerdict(
                dimension=dim, method_signals=signals,
                consensus=unique[0] if unique else "",
                confidence="high" if len(signals) >= self._min_agreement else "medium",
                best_method=METHOD_DISPLAY.get(best, best),
            )

        conflicts = []
        for m1, s1 in signals.items():
            for m2, s2 in signals.items():
                if m1 < m2 and s1.strip() != s2.strip():
                    conflicts.append(f"{METHOD_DISPLAY.get(m1,m1)} 与 {METHOD_DISPLAY.get(m2,m2)} 分歧")

        return DimensionVerdict(
            dimension=dim, method_signals=signals,
            consensus=unique[0], confidence="medium",
            conflicts=conflicts, best_method=METHOD_DISPLAY.get(best, best),
        )

    def _generate_final(self, verdicts: list[DimensionVerdict], runnable: list[MethodResult]) -> str:
        names = ", ".join(METHOD_DISPLAY.get(r.method, r.method) for r in runnable)
        high = [v for v in verdicts if v.confidence == "high"]
        conflict = [v for v in verdicts if v.conflicts]

        parts = [f"基于 {names} 的交叉分析。"]
        if high:
            parts.append(f"高置信度：{'、'.join(DIMENSION_LABELS.get(v.dimension,v.dimension) for v in high)}。")
        if conflict:
            parts.append(f"分歧维度：{'、'.join(DIMENSION_LABELS.get(v.dimension,v.dimension) for v in conflict)}，以{conflict[0].best_method}为主。")
        return " ".join(parts)
