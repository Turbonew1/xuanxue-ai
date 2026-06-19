"""金口诀排盘引擎"""

from __future__ import annotations

from datetime import datetime
from typing import Any

TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
TIAN_GAN_WX = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
               "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
DI_ZHI_WX = {"子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
             "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"}
GUI_SHEN_START = {
    "甲": "未", "乙": "申", "丙": "酉", "丁": "亥", "戊": "子",
    "己": "丑", "庚": "寅", "辛": "卯", "壬": "巳", "癸": "午",
}
GUI_SHEN = ["贵神", "腾蛇", "朱雀", "六合", "勾陈", "青龙",
            "天空", "白虎", "太常", "玄武", "太阴", "天后"]


def _hour_zhi(dt: datetime) -> str:
    return DI_ZHI[(dt.hour + 1) // 2 % 12]


def calculate_jinkou(input_data: dict[str, Any]) -> dict[str, Any]:
    birth_str = input_data.get("birth_datetime", "")
    dt = datetime.strptime(birth_str, "%Y-%m-%d %H:%M")

    base = datetime(2000, 1, 7)
    day_gan = TIAN_GAN[(dt.date() - base.date()).days % 10]
    day_zhi = DI_ZHI[(dt.date() - base.date()).days % 12]
    hour_zhi = _hour_zhi(dt)

    di_fen = hour_zhi
    yue_jiang_idx = (dt.month + 1) % 12
    yue_jiang = DI_ZHI[yue_jiang_idx]

    gui_start = GUI_SHEN_START.get(day_gan, "未")
    gui_start_idx = DI_ZHI.index(gui_start)
    hour_idx = DI_ZHI.index(hour_zhi)
    gui_shen = GUI_SHEN[(gui_start_idx + hour_idx) % 12]

    return {
        "di_fen": di_fen, "di_fen_wx": DI_ZHI_WX.get(di_fen, ""),
        "yue_jiang": yue_jiang, "yue_jiang_wx": DI_ZHI_WX.get(yue_jiang, ""),
        "gui_shen": gui_shen,
        "ren_yuan": day_gan, "ren_yuan_wx": TIAN_GAN_WX.get(day_gan, ""),
        "day_gan": day_gan, "day_zhi": day_zhi, "hour_zhi": hour_zhi,
    }
