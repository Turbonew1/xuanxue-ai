"""农历↔公历转换工具"""

from __future__ import annotations

from datetime import datetime

from lunardate import LunarDate


def lunar_to_solar(year: int, month: int, day: int) -> datetime:
    """农历→公历"""
    ld = LunarDate(year, month, day)
    return ld.toSolarDate()


def is_valid_lunar_date(year: int, month: int, day: int) -> bool:
    """验证农历日期是否合法"""
    try:
        LunarDate(year, month, day)
        return True
    except ValueError:
        return False
