"""技法注册表 — 管理所有可用的命理方法

设计原则（取自 Numerologist_skills）：
- 确定性计算外包给 calculators/
- LLM 只做解读
- 每个方法声明自己的状态：runnable / partial / blocked
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


class MethodStatus(str, Enum):
    """方法运行状态"""

    RUNNABLE = "runnable"  # 可完整运行
    PARTIAL = "partial"  # 部分数据可用
    BLOCKED = "blocked"  # 无法运行（缺数据或无法排盘）


@dataclass(frozen=True)
class MethodResult:
    """单个方法的计算结果"""

    method: str
    status: MethodStatus
    facts: dict[str, Any] = field(default_factory=dict)
    interpretation: str = ""
    confidence: str = "medium"
    blockers: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)


@dataclass
class MethodEntry:
    """注册表中的方法条目"""

    name: str
    display_name: str
    description: str
    calculator: Optional[Callable] = None
    analyzer_prompt: Optional[str] = None
    required_fields: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)


class MethodRegistry:
    """技法注册表 — 管理所有命理方法的注册、状态检查、计算调度"""

    def __init__(self) -> None:
        self._methods: dict[str, MethodEntry] = {}

    def register(self, entry: MethodEntry) -> None:
        """注册一个命理方法"""
        self._methods[entry.name] = entry

    def get(self, name: str) -> Optional[MethodEntry]:
        """获取方法条目"""
        return self._methods.get(name)

    def list_all(self) -> list[MethodEntry]:
        """列出所有已注册方法"""
        return list(self._methods.values())

    def check_status(
        self, name: str, input_data: dict[str, Any]
    ) -> MethodStatus:
        """检查方法在当前输入下是否可运行"""
        entry = self._methods.get(name)
        if entry is None:
            return MethodStatus.BLOCKED

        # 检查必要字段
        for field_name in entry.required_fields:
            value = input_data.get(field_name)
            if value is None or value == "" or value == "unknown":
                return MethodStatus.PARTIAL if len(entry.required_fields) > 1 else MethodStatus.BLOCKED

        # 检查依赖方法
        for dep in entry.depends_on:
            dep_status = self.check_status(dep, input_data)
            if dep_status == MethodStatus.BLOCKED:
                return MethodStatus.BLOCKED

        return MethodStatus.RUNNABLE

    def run_method(
        self, name: str, input_data: dict[str, Any]
    ) -> MethodResult:
        """运行指定方法，返回结果"""
        entry = self._methods.get(name)
        if entry is None:
            return MethodResult(
                method=name,
                status=MethodStatus.BLOCKED,
                blockers=[f"方法 '{name}' 未注册"],
            )

        status = self.check_status(name, input_data)
        if status == MethodStatus.BLOCKED:
            missing = [
                f for f in entry.required_fields
                if not input_data.get(f)
            ]
            return MethodResult(
                method=name,
                status=status,
                blockers=[f"缺少必要字段: {', '.join(missing)}"] if missing else ["数据不足"],
            )

        if entry.calculator is None:
            return MethodResult(
                method=name,
                status=MethodStatus.BLOCKED,
                blockers=["计算器未实现"],
            )

        try:
            facts = entry.calculator(input_data)
            return MethodResult(
                method=name,
                status=status,
                facts=facts,
                confidence="high" if status == MethodStatus.RUNNABLE else "medium",
            )
        except Exception as e:
            return MethodResult(
                method=name,
                status=MethodStatus.BLOCKED,
                blockers=[f"计算出错: {e}"],
            )


# 全局注册表实例
registry = MethodRegistry()
