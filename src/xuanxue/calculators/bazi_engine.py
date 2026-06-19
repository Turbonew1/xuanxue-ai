"""八字排盘引擎

基于 shizhilya/yuan 的 bazi_skill_engine.py 简化重构。
核心原则：所有排盘计算由确定性算法完成，LLM 只做后续解读。

参考典籍：
- 穷通宝典（调候用神）
- 三命通会（格局论断）
- 滴天髓（日主旺衰）
- 渊海子平（十神六亲）
- 子平真诠（格局成败）
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

# ============================================================
# 基础数据表
# ============================================================

TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

WUXING_OF_GAN = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}
WUXING_OF_ZHI = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土",
    "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金",
    "戌": "土", "亥": "水",
}

YIN_YANG_OF_GAN = {
    "甲": "阳", "乙": "阴", "丙": "阳", "丁": "阴", "戊": "阳",
    "己": "阴", "庚": "阳", "辛": "阴", "壬": "阳", "癸": "阴",
}

# 十神表：(日干, 其他干) → 十神
SHISHEN_TABLE: dict[tuple[str, str], str] = {}
_SHISHEN_ORDER = ["比肩", "劫财", "食神", "伤官", "偏财", "正财", "七杀", "正官", "偏印", "正印"]
_GAN_WUXING_ORDER = ["木", "火", "土", "金", "水"]

for _i, _gan in enumerate(TIAN_GAN):
    _ri_wx = WUXING_OF_GAN[_gan]
    _ri_idx = _GAN_WUXING_ORDER.index(_ri_wx)
    _ri_yy = YIN_YANG_OF_GAN[_gan]
    for _j, _other in enumerate(TIAN_GAN):
        _other_wx = WUXING_OF_GAN[_other]
        _other_yy = YIN_YANG_OF_GAN[_other]
        _other_idx = _GAN_WUXING_ORDER.index(_other_wx)
        _diff = (_other_idx - _ri_idx) % 5
        if _diff == 0:
            SHISHEN_TABLE[(_gan, _other)] = "比肩" if _ri_yy == _other_yy else "劫财"
        elif _diff == 1:
            SHISHEN_TABLE[(_gan, _other)] = "食神" if _ri_yy == _other_yy else "伤官"
        elif _diff == 2:
            SHISHEN_TABLE[(_gan, _other)] = "偏财" if _ri_yy == _other_yy else "正财"
        elif _diff == 3:
            SHISHEN_TABLE[(_gan, _other)] = "七杀" if _ri_yy == _other_yy else "正官"
        elif _diff == 4:
            SHISHEN_TABLE[(_gan, _other)] = "偏印" if _ri_yy == _other_yy else "正印"

# 藏干表
CANG_GAN: dict[str, list[str]] = {
    "子": ["癸"],
    "丑": ["己", "癸", "辛"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "庚", "戊"],
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "辛", "丁"],
    "亥": ["壬", "甲"],
}

# 时辰对照表
SHICHEN_MAP: list[tuple[int, int, str]] = [
    (23, 1, "子"), (1, 3, "丑"), (3, 5, "寅"), (5, 7, "卯"),
    (7, 9, "辰"), (9, 11, "巳"), (11, 13, "午"), (13, 15, "未"),
    (15, 17, "申"), (17, 19, "酉"), (19, 21, "戌"), (21, 23, "亥"),
]

# 节气近似日期
JIEQI_MONTHS: list[tuple[int, str, int]] = [
    (2, "立春", 4), (3, "惊蛰", 6), (4, "清明", 5), (5, "立夏", 6),
    (6, "芒种", 6), (7, "小暑", 7), (8, "立秋", 7), (9, "白露", 8),
    (10, "寒露", 8), (11, "立冬", 7), (0, "大雪", 7), (1, "小寒", 6),
]

# 年上起月法
YEAR_START_MONTH: dict[str, str] = {
    "甲": "丙", "己": "丙", "乙": "戊", "庚": "戊",
    "丙": "庚", "辛": "庚", "丁": "壬", "壬": "壬",
    "戊": "甲", "癸": "甲",
}

# 日上起时法（五鼠遁元）
DAY_START_HOUR: dict[str, str] = {
    "甲": "甲", "己": "甲", "乙": "丙", "庚": "丙",
    "丙": "戊", "辛": "戊", "丁": "庚", "壬": "庚",
    "戊": "壬", "癸": "壬",
}


# ============================================================
# 内部工具函数
# ============================================================

def _time_to_shichen(hour: int, minute: int = 0) -> str:
    t = hour + minute / 60.0
    if t >= 23.0:
        return "子"
    for start, end, zhi in SHICHEN_MAP:
        if start <= t < end:
            return zhi
    return "子"


def _get_year_gan_zhi(year: int, month: int, day: int) -> str:
    li_chun_day = 4
    if month < 2 or (month == 2 and day < li_chun_day):
        year -= 1
    gan_idx = (year - 4) % 10
    zhi_idx = (year - 4) % 12
    return TIAN_GAN[gan_idx] + DI_ZHI[zhi_idx]


def _get_month_gan_zhi(year_gan: str, month: int, day: int) -> str:
    zhi_idx = 2
    for idx, _name, jie_day in JIEQI_MONTHS:
        if month == 2 and day < jie_day:
            zhi_idx = 1
            break
        if month == 2 and day >= jie_day:
            zhi_idx = 2
            break
        if idx == 2 and month == 2:
            zhi_idx = 2
            break

    start_gan = YEAR_START_MONTH.get(year_gan, "甲")
    start_gan_idx = TIAN_GAN.index(start_gan)
    month_gan_idx = (start_gan_idx + zhi_idx - 2) % 10
    month_gan = TIAN_GAN[month_gan_idx]
    return month_gan + DI_ZHI[zhi_idx]


def _get_day_gan_zhi(year: int, month: int, day: int) -> str:
    anchor = datetime(1900, 1, 1)
    target = datetime(year, month, day)
    delta = (target - anchor).days
    gan_idx = delta % 10
    zhi_idx = (delta + 10) % 12
    return TIAN_GAN[gan_idx] + DI_ZHI[zhi_idx]


def _get_hour_gan_zhi(day_gan: str, hour_zhi: str) -> str:
    start_gan = DAY_START_HOUR.get(day_gan, "甲")
    start_gan_idx = TIAN_GAN.index(start_gan)
    hour_zhi_idx = DI_ZHI.index(hour_zhi)
    hour_gan_idx = (start_gan_idx + hour_zhi_idx) % 10
    return TIAN_GAN[hour_gan_idx] + hour_zhi


def _compute_shishen(ri_gan: str, other_gan: str) -> str:
    return SHISHEN_TABLE.get((ri_gan, other_gan), "?")


def _count_wuxing(pillars: list[str]) -> dict[str, int]:
    count: dict[str, int] = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for gz in pillars:
        gan, zhi = gz[0], gz[1]
        count[WUXING_OF_GAN[gan]] += 2
        count[WUXING_OF_ZHI[zhi]] += 1
        for cg in CANG_GAN.get(zhi, []):
            count[WUXING_OF_GAN[cg]] += 1
    return count


def _determine_dayun_direction(year_gan: str, gender: str) -> str:
    yy = YIN_YANG_OF_GAN[year_gan]
    if (yy == "阳" and gender == "male") or (yy == "阴" and gender == "female"):
        return "forward"
    return "backward"


def _generate_dayun(month_gz: str, direction: str, count: int = 8) -> list[str]:
    month_gan_idx = TIAN_GAN.index(month_gz[0])
    month_zhi_idx = DI_ZHI.index(month_gz[1])
    step = 1 if direction == "forward" else -1
    dayun: list[str] = []
    for i in range(1, count + 1):
        g_idx = (month_gan_idx + step * i) % 10
        z_idx = (month_zhi_idx + step * i) % 12
        dayun.append(TIAN_GAN[g_idx] + DI_ZHI[z_idx])
    return dayun


# ============================================================
# 主入口
# ============================================================

def calculate_bazi(input_data: dict[str, Any]) -> dict[str, Any]:
    """八字排盘计算

    Args:
        input_data: 统一输入包字典

    Returns:
        包含排盘结果的字典
    """
    bd = input_data["birth_datetime"]
    parts = bd.replace("/", "-").split()
    date_parts = parts[0].split("-")
    year = int(date_parts[0])
    month = int(date_parts[1])
    day = int(date_parts[2])

    time_str = parts[1] if len(parts) > 1 else "12:00"
    time_parts = time_str.split(":")
    hour = int(time_parts[0])
    minute = int(time_parts[1]) if len(time_parts) > 1 else 0

    gender = input_data.get("gender", "male")

    year_gz = _get_year_gan_zhi(year, month, day)
    month_gz = _get_month_gan_zhi(year_gz[0], month, day)
    day_gz = _get_day_gan_zhi(year, month, day)

    if hour >= 23 or (hour == 23 and minute > 0):
        hour_zhi = "子"
        day_gz_next = _get_day_gan_zhi(year, month, day + 1)
        hour_gz = _get_hour_gan_zhi(day_gz_next[0], hour_zhi)
    else:
        hour_zhi = _time_to_shichen(hour, minute)
        hour_gz = _get_hour_gan_zhi(day_gz[0], hour_zhi)

    pillars = [year_gz, month_gz, day_gz, hour_gz]
    ri_gan = day_gz[0]

    shishen = {
        "year": _compute_shishen(ri_gan, year_gz[0]),
        "month": _compute_shishen(ri_gan, month_gz[0]),
        "day": "日主",
        "hour": _compute_shishen(ri_gan, hour_gz[0]),
    }

    cang_gan = {
        "year": CANG_GAN.get(year_gz[1], []),
        "month": CANG_GAN.get(month_gz[1], []),
        "day": CANG_GAN.get(day_gz[1], []),
        "hour": CANG_GAN.get(hour_gz[1], []),
    }

    wuxing = _count_wuxing(pillars)
    direction = _determine_dayun_direction(year_gz[0], gender)
    dayun = _generate_dayun(month_gz, direction)

    return {
        "pillars": {
            "year": year_gz,
            "month": month_gz,
            "day": day_gz,
            "hour": hour_gz,
        },
        "shishen": shishen,
        "cang_gan": cang_gan,
        "wuxing": wuxing,
        "ri_gan": ri_gan,
        "ri_gan_wuxing": WUXING_OF_GAN[ri_gan],
        "dayun": dayun,
        "dayun_direction": "顺排" if direction == "forward" else "逆排",
    }
