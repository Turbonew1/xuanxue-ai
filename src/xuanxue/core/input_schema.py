"""统一输入 Schema — 所有技法共享的输入包

取自 shizhilya/yuan 的统一输入包设计，增加 Pydantic 校验。
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class CalendarType(str, Enum):
    SOLAR = "solar"
    LUNAR = "lunar"
    UNKNOWN = "unknown"


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class BirthInput(BaseModel):
    """统一出生信息输入包"""

    name: str = Field(..., min_length=1, description="姓名")
    gender: Gender = Field(..., description="性别")
    birth_datetime: str = Field(
        ...,
        description="出生日期时间，格式 YYYY-MM-DD HH:MM 或 YYYY-MM-DD",
    )
    calendar_type: CalendarType = Field(
        default=CalendarType.SOLAR,
        description="历法类型：solar/lunar/unknown",
    )
    birthplace: str = Field(
        default="",
        description="出生地，至少到城市，如 '辽宁省丹东市'",
    )
    timezone: str = Field(default="8", description="时区偏移，如 '8' 表示 UTC+8")
    latitude: Optional[float] = Field(default=None, description="出生地纬度")
    longitude: Optional[float] = Field(default=None, description="出生地经度")
    question_focus: list[str] = Field(
        default_factory=list,
        description="用户关注的主题，如 ['事业', '财运', '感情']",
    )
    known_aliases: list[str] = Field(
        default_factory=list, description="曾用名列表"
    )
    alias_change_year: Optional[int] = Field(
        default=None, description="改名大致年份"
    )
    is_alive: bool = Field(default=True, description="在世状态")
    death_year: Optional[int] = Field(default=None, description="去世年份")

    @field_validator("birth_datetime")
    @classmethod
    def validate_datetime(cls, v: str) -> str:
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                datetime.strptime(v, fmt)
                return v
            except ValueError:
                continue
        raise ValueError(
            f"birth_datetime 格式无效: '{v}'，应为 'YYYY-MM-DD HH:MM' 或 'YYYY-MM-DD'"
        )

    def to_dict(self) -> dict:
        """序列化为 JSON 兼容字典"""
        return {
            "name": self.name,
            "gender": self.gender.value,
            "birth_datetime": self.birth_datetime,
            "calendar_type": self.calendar_type.value,
            "birthplace": self.birthplace,
            "timezone": self.timezone,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "question_focus": self.question_focus,
            "known_aliases": self.known_aliases,
            "alias_change_year": self.alias_change_year,
            "is_alive": self.is_alive,
            "death_year": self.death_year,
        }


class StyleMode(str, Enum):
    CONSERVATIVE = "conservative"
    DIRECT = "direct"


class Assertiveness(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class YearWindow(BaseModel):
    """运势输出的年份窗口"""

    anchor_year: int = Field(
        default_factory=lambda: datetime.now().year,
        description="锚定年份，默认当前年",
    )
    past: int = Field(default=2, description="向前几年")
    future: int = Field(default=2, description="向后几年")


class RenderConfig(BaseModel):
    """渲染配置 — 控制输出风格"""

    style_mode: StyleMode = Field(
        default=StyleMode.CONSERVATIVE, description="输出风格"
    )
    assertiveness: Assertiveness = Field(
        default=Assertiveness.MEDIUM, description="断语力度"
    )
    year_window: YearWindow = Field(
        default_factory=YearWindow, description="年份窗口"
    )

    @classmethod
    def from_user_hints(cls, hints: list[str]) -> "RenderConfig":
        """从用户自然语言提示推断渲染配置"""
        hints_text = " ".join(hints).lower()
        style = StyleMode.DIRECT if any(
            w in hints_text for w in ("直断", "详细", "不要摘要", "直接说")
        ) else StyleMode.CONSERVATIVE
        assertiveness = (
            Assertiveness.HIGH if "直断" in hints_text or "详细" in hints_text
            else Assertiveness.MEDIUM
        )
        return cls(style_mode=style, assertiveness=assertiveness)


class AnalysisRequest(BaseModel):
    """完整的分析请求"""

    input: BirthInput
    config: RenderConfig = Field(default_factory=RenderConfig)
    methods: list[str] = Field(
        default_factory=list,
        description="指定运行的方法列表，空则运行所有可用方法",
    )
