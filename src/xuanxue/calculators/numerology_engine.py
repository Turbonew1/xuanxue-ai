"""数字命理引擎 — 五格剖象法 + 生命数"""

from __future__ import annotations

from datetime import datetime
from typing import Any

STROKE_MAP: dict[str, int] = {
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
    "大": 3, "小": 3, "中": 4, "天": 4, "地": 6, "人": 2, "金": 8, "木": 4, "水": 4, "火": 4, "土": 3,
    "明": 8, "华": 14, "国": 11, "家": 10, "德": 15, "才": 4, "文": 4, "武": 8, "英": 11,
    "张": 11, "李": 7, "王": 4, "赵": 14, "刘": 15, "陈": 16, "杨": 13, "黄": 12, "周": 8,
    "吴": 7, "徐": 10, "孙": 6, "马": 10, "朱": 6, "胡": 11, "郭": 15, "林": 8, "何": 7,
    "高": 10, "罗": 20, "梁": 11, "宋": 7, "郑": 19, "谢": 17, "韩": 17, "唐": 10, "冯": 12,
    "于": 3, "董": 15, "程": 12, "曹": 11, "袁": 10, "邓": 19, "许": 11, "傅": 12, "曾": 12,
    "吕": 7, "苏": 22, "卢": 16, "蒋": 17, "蔡": 17, "丁": 2, "魏": 18, "叶": 15, "田": 5,
    "任": 6, "姜": 9, "范": 15, "方": 4, "石": 5, "姚": 9, "谭": 19, "廖": 14, "邹": 17,
    "金": 8, "陆": 16, "孔": 4, "白": 5, "崔": 11, "康": 11, "毛": 4, "秦": 10, "江": 7,
    "史": 5, "侯": 9, "邵": 12, "孟": 8, "龙": 16, "万": 15, "段": 9, "雷": 13, "钱": 16,
    "汤": 13, "尹": 4, "易": 8, "常": 11, "乔": 12, "贺": 12, "赖": 16, "龚": 22, "兰": 23,
    "梅": 11, "玉": 5, "珠": 11, "宝": 20, "福": 14, "禄": 13, "寿": 14, "喜": 12, "安": 6,
    "平": 5, "和": 8, "贵": 12, "富": 12, "荣": 14, "春": 9, "夏": 10, "秋": 9, "冬": 5,
}

GRID_FORTUNE: dict[int, str] = {
    1: "大吉", 3: "大吉", 5: "大吉", 6: "大吉", 7: "吉", 8: "吉",
    11: "大吉", 13: "大吉", 15: "大吉", 16: "大吉", 17: "吉", 18: "吉",
    21: "大吉", 23: "大吉", 24: "大吉", 25: "吉", 29: "吉", 31: "大吉",
    32: "大吉", 33: "大吉", 35: "吉", 37: "吉", 39: "吉", 41: "大吉",
}
UNLUCKY = {2, 4, 9, 10, 12, 14, 19, 20, 22, 26, 27, 28, 30, 34, 36, 38, 40, 42, 43, 44, 46}


def get_strokes(name: str) -> list[int]:
    return [STROKE_MAP.get(c, 10) for c in name if c.strip()]


def _reduce(n: int) -> int:
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(d) for d in str(n))
    return n


def _fortune(n: int) -> str:
    if n in GRID_FORTUNE:
        return GRID_FORTUNE[n]
    if n in UNLUCKY:
        return "凶"
    return "中吉"


def calculate_numerology(input_data: dict[str, Any]) -> dict[str, Any]:
    name = input_data.get("name", "")
    birth_str = input_data.get("birth_datetime", "")
    strokes = get_strokes(name)
    birth = datetime.strptime(birth_str.split()[0], "%Y-%m-%d")

    life_number = _reduce(birth.year + birth.month + birth.day)
    soul_number = _reduce(sum(strokes)) if strokes else 0

    if len(strokes) >= 2:
        ren_ge = _reduce(strokes[0] + strokes[1])
    elif strokes:
        ren_ge = _reduce(strokes[0] * 2)
    else:
        ren_ge = 0

    total_strokes = sum(strokes) if strokes else 0
    tian_ge = strokes[0] + 1 if strokes else 0
    di_ge = _reduce(sum(strokes[1:])) if len(strokes) >= 3 else (_reduce(strokes[1] + 1) if len(strokes) == 2 else tian_ge)
    zong_ge = _reduce(total_strokes) if total_strokes else 0
    wai_ge = _reduce(zong_ge - ren_ge + 1) if zong_ge and ren_ge else 0

    return {
        "name": name, "strokes": strokes,
        "life_number": life_number, "soul_number": soul_number,
        "personality_number": ren_ge, "birth_day": birth.day,
        "tian_ge": tian_ge, "ren_ge": ren_ge, "di_ge": di_ge,
        "wai_ge": wai_ge, "total_grid": zong_ge, "total_strokes": total_strokes,
        "tian_fortune": _fortune(tian_ge), "ren_fortune": _fortune(ren_ge),
        "di_fortune": _fortune(di_ge), "wai_fortune": _fortune(wai_ge),
        "total_fortune": _fortune(zong_ge),
    }
