"""奇门遁甲排盘引擎

基于 Numerologist_skills 的 qimen-dunjia SKILL.md 规则简化实现。
时家转盘奇门，置闰法定局，中宫寄坤。

核心原则：排盘计算由确定性算法完成，LLM 只做格局解读。
"""

from __future__ import annotations

from typing import Any

TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

JIUGONG_NAMES = ["坎一宫", "坤二宫", "震三宫", "巽四宫", "中五宫", "乾六宫", "兑七宫", "艮八宫", "离九宫"]

BA_MEN = ["休门", "死门", "伤门", "杜门", "开门", "惊门", "生门", "景门"]
BA_SHEN = ["值符", "螣蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天"]
JIU_XING = ["天蓬", "天芮", "天冲", "天辅", "天禽", "天心", "天柱", "天任", "天英"]

MEN_ORIGINAL: dict[str, int] = {
    "休门": 0, "死门": 1, "伤门": 2, "杜门": 3,
    "开门": 5, "惊门": 6, "生门": 7, "景门": 8,
}
XING_ORIGINAL: dict[str, int] = {
    "天蓬": 0, "天芮": 1, "天冲": 2, "天辅": 3,
    "天禽": 4, "天心": 5, "天柱": 6, "天任": 7, "天英": 8,
}
SHEN_ORIGINAL: dict[str, int] = {
    "值符": 0, "螣蛇": 1, "太阴": 2, "六合": 3,
    "白虎": 5, "玄武": 6, "九地": 7, "九天": 8,
}

JIEQI_DATES: list[tuple[str, int, int, int]] = [
    ("小寒", 1, 6, 2), ("大寒", 1, 20, 3),
    ("立春", 2, 4, 1), ("雨水", 2, 19, 2),
    ("惊蛰", 3, 6, 1), ("春分", 3, 21, 2),
    ("清明", 4, 5, 1), ("谷雨", 4, 20, 2),
    ("立夏", 5, 6, 1), ("小满", 5, 21, 2),
    ("芒种", 6, 6, 1), ("夏至", 6, 21, 9),
    ("小暑", 7, 7, 8), ("大暑", 7, 23, 7),
    ("立秋", 8, 7, 8), ("处暑", 8, 23, 7),
    ("白露", 9, 8, 8), ("秋分", 9, 23, 7),
    ("寒露", 10, 8, 8), ("霜降", 10, 23, 7),
    ("立冬", 11, 7, 8), ("小雪", 11, 22, 7),
    ("大雪", 12, 7, 8), ("冬至", 12, 22, 1),
]

XUNSHOU_TABLE: list[tuple[str, str]] = [
    ("甲子", "戊"), ("甲戌", "己"), ("甲申", "庚"),
    ("甲午", "辛"), ("甲辰", "壬"), ("甲寅", "癸"),
]


def _get_year_gan_zhi(year: int) -> str:
    return TIAN_GAN[(year - 4) % 10] + DI_ZHI[(year - 4) % 12]


def _get_month_gan_zhi(year_gan: str, month: int) -> str:
    year_start = {"甲":"丙","己":"丙","乙":"戊","庚":"戊","丙":"庚",
                  "辛":"庚","丁":"壬","壬":"壬","戊":"甲","癸":"甲"}
    start_idx = TIAN_GAN.index(year_start.get(year_gan, "甲"))
    zhi_idx = (month + 1) % 12
    return TIAN_GAN[(start_idx + zhi_idx - 2) % 10] + DI_ZHI[zhi_idx]


def _get_day_gan_zhi(year: int, month: int, day: int) -> str:
    from datetime import datetime
    delta = (datetime(year, month, day) - datetime(1900, 1, 1)).days
    return TIAN_GAN[delta % 10] + DI_ZHI[(delta + 10) % 12]


def _get_hour_gan_zhi(day_gan: str, hour_zhi: str) -> str:
    day_start = {"甲":"甲","己":"甲","乙":"丙","庚":"丙","丙":"戊",
                 "辛":"戊","丁":"庚","壬":"庚","戊":"壬","癸":"壬"}
    start_idx = TIAN_GAN.index(day_start.get(day_gan, "甲"))
    return TIAN_GAN[(start_idx + DI_ZHI.index(hour_zhi)) % 10] + hour_zhi


def _hour_to_zhi(hour: int, minute: int = 0) -> str:
    t = hour + minute / 60.0
    if t >= 23.0:
        return "子"
    for s, e, z in [(23,1,"子"),(1,3,"丑"),(3,5,"寅"),(5,7,"卯"),(7,9,"辰"),
                     (9,11,"巳"),(11,13,"午"),(13,15,"未"),(15,17,"申"),
                     (17,19,"酉"),(19,21,"戌"),(21,23,"亥")]:
        if s <= t < e:
            return z
    return "子"


def _determine_ju(month: int, day: int) -> int:
    for _name, jm, jd, base in JIEQI_DATES:
        if month == jm and day >= jd:
            return base
    return 4


def _determine_dun_type(year_gan: str) -> str:
    yy = "阳" if TIAN_GAN.index(year_gan) % 2 == 0 else "阴"
    return "阳遁" if yy == "阳" else "阴遁"


def _find_xunshou(hour_gan_zhi: str) -> tuple[str, str]:
    h_zhi_idx = DI_ZHI.index(hour_gan_zhi[1])
    for xunshou_gz, hidden_gan in XUNSHOU_TABLE:
        xs_zhi_idx = DI_ZHI.index(xunshou_gz[1])
        if (h_zhi_idx - xs_zhi_idx) % 12 <= 9:
            return xunshou_gz, hidden_gan
    return "甲子", "戊"


def _place_qi_yi(ju: int, dun_type: str) -> list[str]:
    qi_yi = list(TIAN_GAN)
    if dun_type == "阴遁":
        qi_yi = list(reversed(qi_yi))
    return [qi_yi[(i + ju - 1) % 10] for i in range(9)]


def _place_men(ju: int) -> dict[str, int]:
    return {m: (o + ju - 1) % 9 for m, o in MEN_ORIGINAL.items()}


def _place_xing(ju: int) -> dict[str, int]:
    return {x: (o + ju - 1) % 9 for x, o in XING_ORIGINAL.items()}


def _place_shen(ju: int) -> dict[str, int]:
    return {s: (o + ju - 1) % 9 for s, o in SHEN_ORIGINAL.items()}


def calculate_qimen(input_data: dict[str, Any]) -> dict[str, Any]:
    """奇门遁甲排盘计算"""
    bd = input_data["birth_datetime"]
    parts = bd.replace("/", "-").split()
    dp = parts[0].split("-")
    year, month, day = int(dp[0]), int(dp[1]), int(dp[2])

    time_str = parts[1] if len(parts) > 1 else "12:00"
    tp = time_str.split(":")
    hour, minute = int(tp[0]), int(tp[1]) if len(tp) > 1 else 0

    year_gz = _get_year_gan_zhi(year)
    month_gz = _get_month_gan_zhi(year_gz[0], month)
    day_gz = _get_day_gan_zhi(year, month, day)
    hour_zhi = _hour_to_zhi(hour, minute)
    hour_gz = _get_hour_gan_zhi(day_gz[0], hour_zhi)

    ju = _determine_ju(month, day)
    dun_type = _determine_dun_type(year_gz[0])
    xunshou, hidden_gan = _find_xunshou(hour_gz)

    qi_yi = _place_qi_yi(ju, dun_type)
    men = _place_men(ju)
    xing = _place_xing(ju)
    shen = _place_shen(ju)

    palaces = []
    for i in range(9):
        palace_men = [m for m, p in men.items() if p == i]
        palace_xing = [x for x, p in xing.items() if p == i]
        palace_shen = [s for s, p in shen.items() if p == i]
        palaces.append({
            "palace": i + 1, "name": JIUGONG_NAMES[i],
            "qi_yi": qi_yi[i], "men": palace_men[0] if palace_men else None,
            "xing": palace_xing[0] if palace_xing else None,
            "shen": palace_shen[0] if palace_shen else None,
            "is_center": i == 4, "hosts_center": i == 1,
        })

    return {
        "ganzhi": {"year": year_gz, "month": month_gz, "day": day_gz, "hour": hour_gz},
        "ju": ju, "dun_type": dun_type, "xunshou": xunshou,
        "hidden_gan": hidden_gan, "palaces": palaces,
    }
