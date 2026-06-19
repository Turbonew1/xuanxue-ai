"""自然语言调度器 — 根据用户请求选择合适的命理方法

取自 Yuan 的调度理念 + Horosa 的 dispatch 模式。
"""

from __future__ import annotations

from typing import Any

from xuanxue.core.registry import MethodRegistry, MethodResult, MethodStatus


# 关键词到方法的映射
KEYWORD_MAP: dict[str, list[str]] = {
    # 八字
    "八字": ["bazi"],
    "四柱": ["bazi"],
    "命理": ["bazi"],
    "bazi": ["bazi"],
    "算命": ["bazi", "ziwei", "chenggu"],
    # 紫微斗数
    "紫微": ["ziwei"],
    "紫微斗数": ["ziwei"],
    "ziwei": ["ziwei"],
    # 奇门遁甲
    "奇门": ["qimen"],
    "奇门遁甲": ["qimen"],
    "qimen": ["qimen"],
    # 称骨
    "称骨": ["chenggu"],
    "称骨算命": ["chenggu"],
    # 西方占星
    "占星": ["western"],
    "星盘": ["western"],
    "astrology": ["western"],
    # 吠陀占星
    "吠陀": ["vedic"],
    "vedic": ["vedic"],
    # 数字命理
    "数字命理": ["numerology"],
    "numerology": ["numerology"],
    # 大六壬
    "六壬": ["liuren"],
    "大六壬": ["liuren"],
    # 六爻
    "六爻": ["liuyao"],
    "梅花": ["liuyao"],
    "易卦": ["liuyao"],
    # 太乙
    "太乙": ["taiyi"],
    "太乙神数": ["taiyi"],
    # 金口诀
    "金口诀": ["jinkou"],
}


def resolve_methods(
    user_query: str,
    registry: MethodRegistry,
    input_data: dict[str, Any],
) -> list[MethodResult]:
    """根据用户自然语言查询，解析并运行命理方法

    Args:
        user_query: 用户的自然语言查询
        registry: 方法注册表
        input_data: 统一输入包

    Returns:
        各方法的计算结果列表
    """
    # 从查询中提取关键词
    matched_methods: set[str] = set()
    query_lower = user_query.lower()

    for keywords, methods in KEYWORD_MAP.items():
        if keywords in query_lower:
            matched_methods.update(methods)

    # 如果没有匹配到特定方法，运行所有可运行的方法
    if not matched_methods:
        all_entries = registry.list_all()
        matched_methods = {e.name for e in all_entries}

    # 过滤掉注册表中不存在的方法
    available = {e.name for e in registry.list_all()}
    matched_methods &= available

    # 按依赖顺序运行
    results: list[MethodResult] = []
    for method_name in sorted(matched_methods):
        result = registry.run_method(method_name, input_data)
        results.append(result)

    return results


def select_for_full_reading(
    registry: MethodRegistry,
    input_data: dict[str, Any],
    min_methods: int = 3,
) -> list[str]:
    """为完整命理分析选择方法列表

    目标：至少选 min_methods 个 runnable 方法。
    优先选择信息完整度高的方法。
    """
    candidates: list[tuple[str, MethodStatus]] = []

    for entry in registry.list_all():
        status = registry.check_status(entry.name, input_data)
        candidates.append((entry.name, status))

    # 按状态排序：runnable > partial > blocked
    status_order = {
        MethodStatus.RUNNABLE: 0,
        MethodStatus.PARTIAL: 1,
        MethodStatus.BLOCKED: 2,
    }
    candidates.sort(key=lambda x: (status_order.get(x[1], 2), x[0]))

    selected = [name for name, status in candidates if status != MethodStatus.BLOCKED]

    # 如果 runnable 不够，补上 partial
    if len(selected) < min_methods:
        for name, status in candidates:
            if name not in selected and status == MethodStatus.PARTIAL:
                selected.append(name)
            if len(selected) >= min_methods:
                break

    return selected[:max(min_methods, 6)]
