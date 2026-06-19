"""梅花易数引擎 — 时间起卦"""

from __future__ import annotations

from datetime import datetime
from typing import Any

BAGUA_NAMES = ["坤", "震", "坎", "兑", "艮", "离", "巽", "乾"]
BAGUA_SYMBOLS = ["☷", "☳", "☵", "☱", "☶", "☲", "☴", "☰"]
BAGUA_WUXING = ["土", "木", "水", "金", "土", "火", "木", "金"]

GUA64: dict[tuple[int, int], str] = {
    (0, 0): "坤为地", (0, 1): "地雷复", (0, 2): "地水师", (0, 3): "地泽临",
    (0, 4): "地山谦", (0, 5): "地火明夷", (0, 6): "地风升", (0, 7): "地天泰",
    (1, 0): "雷地豫", (1, 1): "震为雷", (1, 2): "雷水解", (1, 3): "雷泽归妹",
    (1, 4): "雷山小过", (1, 5): "雷火丰", (1, 6): "雷风恒", (1, 7): "雷天大壮",
    (2, 0): "水地比", (2, 1): "水雷屯", (2, 2): "坎为水", (2, 3): "水泽节",
    (2, 4): "水山蹇", (2, 5): "水火既济", (2, 6): "水风井", (2, 7): "水天需",
    (3, 0): "泽地萃", (3, 1): "泽雷随", (3, 2): "泽水困", (3, 3): "兑为泽",
    (3, 4): "泽山咸", (3, 5): "泽火革", (3, 6): "泽风大过", (3, 7): "泽天夬",
    (4, 0): "山地剥", (4, 1): "山雷颐", (4, 2): "山水蒙", (4, 3): "山泽损",
    (4, 4): "艮为山", (4, 5): "山火贲", (4, 6): "山风蛊", (4, 7): "山天大畜",
    (5, 0): "火地晋", (5, 1): "火雷噬嗑", (5, 2): "火水未济", (5, 3): "火泽睽",
    (5, 4): "火山旅", (5, 5): "离为火", (5, 6): "火风鼎", (5, 7): "火天大有",
    (6, 0): "风地观", (6, 1): "风雷益", (6, 2): "风水涣", (6, 3): "风泽中孚",
    (6, 4): "风山渐", (6, 5): "风火家人", (6, 6): "巽为风", (6, 7): "风天小畜",
    (7, 0): "天地否", (7, 1): "天雷无妄", (7, 2): "天水讼", (7, 3): "天泽履",
    (7, 4): "天山遁", (7, 5): "天火同人", (7, 6): "天风姤", (7, 7): "乾为天",
}

WUXING_CYCLE = {"金": "水", "水": "木", "木": "火", "火": "土", "土": "金"}
WUXING_KILL = {"金": "木", "木": "土", "土": "水", "水": "火", "火": "金"}


def _ti_yong_relation(ti_wx: str, yong_wx: str) -> str:
    if ti_wx == yong_wx:
        return "比和"
    if WUXING_CYCLE.get(ti_wx) == yong_wx:
        return "体生用，泄气"
    if WUXING_CYCLE.get(yong_wx) == ti_wx:
        return "用生体，得助"
    if WUXING_KILL.get(ti_wx) == yong_wx:
        return "体克用，有利"
    if WUXING_KILL.get(yong_wx) == ti_wx:
        return "用克体，不利"
    return "未知"


def calculate_meihua(input_data: dict[str, Any]) -> dict[str, Any]:
    birth_str = input_data.get("birth_datetime", "")
    dt = datetime.strptime(birth_str, "%Y-%m-%d %H:%M")

    year_zhi_num = (dt.year - 4) % 12 + 1
    month = dt.month
    day = dt.day
    hour = dt.hour
    hour_zhi_num = (hour + 1) // 2 % 12 + 1

    shang_raw = (year_zhi_num + month + day) % 8
    shang_gua = shang_raw if shang_raw != 0 else 8
    shang_idx = shang_gua - 1

    xia_raw = (year_zhi_num + month + day + hour_zhi_num) % 8
    xia_gua = xia_raw if xia_raw != 0 else 8
    xia_idx = xia_gua - 1

    dong_yao_raw = (year_zhi_num + month + day + hour_zhi_num) % 6
    dong_yao = dong_yao_raw if dong_yao_raw != 0 else 6

    gua_name = GUA64.get((xia_idx, shang_idx), "未知")
    hu_name = GUA64.get((xia_idx, shang_idx), "未知")  # 简化

    bian_shang = shang_idx
    bian_xia = xia_idx
    if dong_yao <= 3:
        bian_xia ^= 1
    else:
        bian_shang ^= 1
    bian_name = GUA64.get((bian_xia, bian_shang), "未知")

    if dong_yao <= 3:
        ti_idx, yong_idx = shang_idx, xia_idx
    else:
        ti_idx, yong_idx = xia_idx, shang_idx

    ti_wx = BAGUA_WUXING[ti_idx]
    yong_wx = BAGUA_WUXING[yong_idx]

    return {
        "shang_gua": f"{BAGUA_NAMES[shang_idx]}{BAGUA_SYMBOLS[shang_idx]}",
        "xia_gua": f"{BAGUA_NAMES[xia_idx]}{BAGUA_SYMBOLS[xia_idx]}",
        "ben_gua": gua_name, "hu_gua": hu_name, "bian_gua": bian_name,
        "dong_yao": dong_yao,
        "ti_gua": f"{BAGUA_NAMES[ti_idx]}({ti_wx})",
        "yong_gua": f"{BAGUA_NAMES[yong_idx]}({yong_wx})",
        "ti_yong_relation": _ti_yong_relation(ti_wx, yong_wx),
        "year_zhi_num": year_zhi_num, "month": month, "day": day,
        "hour_zhi_num": hour_zhi_num,
    }
