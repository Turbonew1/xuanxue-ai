"""大六壬排盘引擎 — 月将加时起课"""

from __future__ import annotations

from datetime import datetime
from typing import Any

TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

MONTH_GENERAL = {
    1: "亥", 2: "戌", 3: "酉", 4: "申", 5: "未", 6: "午",
    7: "巳", 8: "辰", 9: "卯", 10: "寅", 11: "丑", 12: "子",
}

GUI_SHEN_START = {
    "甲": "未", "乙": "申", "丙": "酉", "丁": "亥", "戊": "子",
    "己": "丑", "庚": "寅", "辛": "卯", "壬": "巳", "癸": "午",
}


def _get_month_zhi(dt: datetime) -> str:
    return DI_ZHI[(dt.month + 1) % 12]


def _get_hour_zhi(dt: datetime) -> str:
    return DI_ZHI[(dt.hour + 1) // 2 % 12]


def _get_day_gan(dt: datetime) -> str:
    base = datetime(2000, 1, 7)
    return TIAN_GAN[(dt.date() - base.date()).days % 10]


def _get_day_zhi(dt: datetime) -> str:
    base = datetime(2000, 1, 7)
    return DI_ZHI[(dt.date() - base.date()).days % 12]


def calculate_liuren(input_data: dict[str, Any]) -> dict[str, Any]:
    birth_str = input_data.get("birth_datetime", "")
    dt = datetime.strptime(birth_str, "%Y-%m-%d %H:%M")

    month_zhi = _get_month_zhi(dt)
    hour_zhi = _get_hour_zhi(dt)
    day_gan = _get_day_gan(dt)
    day_zhi = _get_day_zhi(dt)

    yue_jiang = MONTH_GENERAL.get(dt.month, "亥")

    tian_pan = {}
    for i, zhi in enumerate(DI_ZHI):
        tian_pan[zhi] = DI_ZHI[(i + DI_ZHI.index(yue_jiang) - DI_ZHI.index(hour_zhi)) % 12]

    si_ke = {
        "第一课": f"{day_gan}上{tian_pan.get(day_zhi, day_zhi)}",
        "第二课": f"{day_zhi}上{tian_pan.get(day_zhi, day_zhi)}",
    }

    return {
        "yue_jiang": yue_jiang, "month_zhi": month_zhi,
        "hour_zhi": hour_zhi, "day_gan": day_gan, "day_zhi": day_zhi,
        "tian_pan": tian_pan, "si_ke": si_ke,
    }
