"""核心模块：输入 Schema、注册表、调度器、综合分析"""

from xuanxue.core.input_schema import BirthInput, RenderConfig, AnalysisRequest
from xuanxue.core.registry import MethodRegistry, MethodStatus
from xuanxue.core.dispatcher import resolve_methods, select_for_full_reading
from xuanxue.core.synthesis import SynthesisEngine
from xuanxue.core import methods  # noqa: F401 — triggers auto-registration

__all__ = [
    "BirthInput",
    "RenderConfig",
    "AnalysisRequest",
    "MethodRegistry",
    "MethodStatus",
    "resolve_methods",
    "select_for_full_reading",
    "SynthesisEngine",
]
