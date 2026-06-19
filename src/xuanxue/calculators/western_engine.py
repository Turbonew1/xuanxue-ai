"""西方占星引擎 — 简化太阳/月亮/上升星座"""

from __future__ import annotations

from datetime import datetime
from typing import Any

SUN_SIGN_DATES = [
    (1, 20, "摩羯座"), (2, 19, "水瓶座"), (3, 21, "双鱼座"), (4, 20, "白羊座"),
    (5, 21, "金牛座"), (6, 22, "双子座"), (7, 23, "巨蟹座"), (8, 23, "狮子座"),
    (9, 23, "处女座"), (10, 24, "天秤座"), (11, 23, "天蝎座"), (12, 22, "射手座"),
]

ELEMENTS = {
    "白羊座": "火", "狮子座": "火", "射手座": "火",
    "金牛座": "土", "处女座": "土", "摩羯座": "土",
    "双子座": "风", "天秤座": "风", "水瓶座": "风",
    "巨蟹座": "水", "天蝎座": "水", "双鱼座": "水",
}

QUALITIES = {
    "白羊座": "开创", "巨蟹座": "开创", "天秤座": "开创", "摩羯座": "开创",
    "金牛座": "固定", "狮子座": "固定", "天蝎座": "固定", "水瓶座": "固定",
    "双子座": "变动", "处女座": "变动", "射手座": "变动", "双鱼座": "变动",
}

SIGNS = ["白羊座", "金牛座", "双子座", "巨蟹座", "狮子座", "处女座",
         "天秤座", "天蝎座", "射手座", "摩羯座", "水瓶座", "双鱼座"]


def _get_sun_sign(month: int, day: int) -> str:
    for m, d, cn in SUN_SIGN_DATES:
        if (month == m and day >= d) or (month == m + 1 and day < d):
            return cn
    return "射手座"


def _get_moon_sign(year: int, month: int, day: int) -> str:
    total_days = year * 365 + month * 30 + day
    return SIGNS[total_days % 12]


def _get_rising_sign(month: int, day: int, hour: int) -> str:
    total = month * 31 + day + hour
    return SIGNS[total % 12]


def calculate_western(input_data: dict[str, Any]) -> dict[str, Any]:
    birth_str = input_data.get("birth_datetime", "")
    dt = datetime.strptime(birth_str, "%Y-%m-%d %H:%M")

    sun_sign = _get_sun_sign(dt.month, dt.day)
    moon_sign = _get_moon_sign(dt.year, dt.month, dt.day)
    rising_sign = _get_rising_sign(dt.month, dt.day, dt.hour)

    element_count = {"火": 0, "土": 0, "风": 0, "水": 0}
    for sign in [sun_sign, moon_sign, rising_sign]:
        el = ELEMENTS.get(sign, "")
        if el in element_count:
            element_count[el] += 1

    return {
        "sun_sign": sun_sign, "sun_element": ELEMENTS.get(sun_sign, ""),
        "moon_sign": moon_sign, "moon_element": ELEMENTS.get(moon_sign, ""),
        "rising_sign": rising_sign, "rising_element": ELEMENTS.get(rising_sign, ""),
        "quality": QUALITIES.get(sun_sign, ""),
        "element_distribution": element_count,
    }
