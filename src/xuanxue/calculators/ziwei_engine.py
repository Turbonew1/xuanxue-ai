"""紫微斗数排盘引擎

基于 Numerologist_skills 的 ziwei-doushu SKILL.md 规则简化实现。
核心原则：排盘计算由确定性算法完成，LLM 只做宫位解读。

参考：三合派排盘口径
"""

from __future__ import annotations

from typing import Any

TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

PALACE_NAMES = [
    "命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄",
    "迁移", "交友", "官禄", "田宅", "福德", "父母",
]

WUXING_JU = {"水二局": 2, "木三局": 3, "金四局": 4, "土五局": 5, "火六局": 6}

SIHUA_TABLE: dict[str, dict[str, str]] = {
    "甲": {"禄": "廉贞", "权": "破军", "科": "武曲", "忌": "太阳"},
    "乙": {"禄": "天机", "权": "天梁", "科": "紫微", "忌": "太阴"},
    "丙": {"禄": "天同", "权": "天机", "科": "文昌", "忌": "廉贞"},
    "丁": {"禄": "太阴", "权": "天同", "科": "天机", "忌": "巨门"},
    "戊": {"禄": "贪狼", "权": "太阴", "科": "右弼", "忌": "天机"},
    "己": {"禄": "武曲", "权": "贪狼", "科": "天梁", "忌": "文曲"},
    "庚": {"禄": "太阳", "权": "武曲", "科": "太阴", "忌": "天同"},
    "辛": {"禄": "巨门", "权": "太阳", "科": "文曲", "忌": "文昌"},
    "壬": {"禄": "天梁", "权": "紫微", "科": "左辅", "忌": "武曲"},
    "癸": {"禄": "破军", "权": "巨门", "科": "太阴", "忌": "贪狼"},
}

SANFANG_SIZHENG: dict[str, dict[str, str]] = {
    "命宫": {"对宫": "迁移", "三合1": "财帛", "三合2": "官禄"},
    "兄弟": {"对宫": "交友", "三合1": "疾厄", "三合2": "田宅"},
    "夫妻": {"对宫": "官禄", "三合1": "迁移", "三合2": "福德"},
    "子女": {"对宫": "田宅", "三合1": "交友", "三合2": "父母"},
    "财帛": {"对宫": "福德", "三合1": "命宫", "三合2": "官禄"},
    "疾厄": {"对宫": "父母", "三合1": "兄弟", "三合2": "田宅"},
    "迁移": {"对宫": "命宫", "三合1": "夫妻", "三合2": "福德"},
    "交友": {"对宫": "兄弟", "三合1": "子女", "三合2": "父母"},
    "官禄": {"对宫": "夫妻", "三合1": "命宫", "三合2": "财帛"},
    "田宅": {"对宫": "子女", "三合1": "兄弟", "三合2": "疾厄"},
    "福德": {"对宫": "财帛", "三合1": "夫妻", "三合2": "迁移"},
    "父母": {"对宫": "疾厄", "三合1": "子女", "三合2": "交友"},
}


def _get_year_gan_zhi(year: int) -> str:
    gan_idx = (year - 4) % 10
    zhi_idx = (year - 4) % 12
    return TIAN_GAN[gan_idx] + DI_ZHI[zhi_idx]


def _get_month_zhi(lunar_month: int) -> str:
    return DI_ZHI[(lunar_month + 1) % 12]


def _get_hour_zhi(hour: int, minute: int = 0) -> str:
    t = hour + minute / 60.0
    if t >= 23.0:
        return "子"
    ranges = [(23,1,"子"),(1,3,"丑"),(3,5,"寅"),(5,7,"卯"),(7,9,"辰"),
              (9,11,"巳"),(11,13,"午"),(13,15,"未"),(15,17,"申"),
              (17,19,"酉"),(19,21,"戌"),(21,23,"亥")]
    for s, e, z in ranges:
        if s <= t < e:
            return z
    return "子"


def _determine_ming_gong(month_zhi: str, hour_zhi: str) -> int:
    month_idx = DI_ZHI.index(month_zhi) if month_zhi in DI_ZHI else 2
    hour_idx = DI_ZHI.index(hour_zhi) if hour_zhi in DI_ZHI else 0
    return (2 + 12 - hour_idx) % 12


def _determine_shen_gong(month_zhi: str, hour_zhi: str) -> int:
    hour_idx = DI_ZHI.index(hour_zhi) if hour_zhi in DI_ZHI else 0
    return (2 + hour_idx) % 12


def _determine_wuxing_ju(ming_zhi: str) -> str:
    zhi_wx = {"子":"水","丑":"土","寅":"木","卯":"木","辰":"土","巳":"火",
              "午":"火","未":"土","申":"金","酉":"金","戌":"土","亥":"水"}
    wx = zhi_wx.get(ming_zhi, "水")
    return {"水":"水二局","木":"木三局","金":"金四局","土":"土五局","火":"火六局"}.get(wx, "水二局")


def _place_main_stars(ming_gong_idx: int, wuxing_ju: str) -> dict[int, list[str]]:
    ju_num = WUXING_JU.get(wuxing_ju, 2)
    palaces: dict[int, list[str]] = {i: [] for i in range(12)}

    ziwei_idx = (ming_gong_idx + ju_num - 1) % 12
    palaces[ziwei_idx].append("紫微")

    ziwei_system = ["天机", "太阳", "武曲", "天同", "廉贞"]
    for i, star in enumerate(ziwei_system):
        idx = (ziwei_idx - 1 - i) % 12
        if star not in palaces[idx]:
            palaces[idx].append(star)

    tianfu_idx = (ziwei_idx + 6) % 12
    palaces[tianfu_idx].append("天府")
    tianfu_system = ["太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军"]
    for i, star in enumerate(tianfu_system):
        idx = (tianfu_idx + 1 + i) % 12
        if star not in palaces[idx]:
            palaces[idx].append(star)

    return palaces


def _apply_sihua(year_gan: str, palaces: dict[int, list[str]]) -> dict[str, str]:
    sihua = SIHUA_TABLE.get(year_gan, {})
    result: dict[str, str] = {}
    for action, star in sihua.items():
        for palace_idx, stars in palaces.items():
            if star in stars:
                result[action] = f"{star}@{PALACE_NAMES[palace_idx]}"
                break
    return result


def _determine_daxian(wuxing_ju: str, gender: str, year_gan: str) -> dict[str, Any]:
    ju_num = WUXING_JU.get(wuxing_ju, 2)
    yy = "阳" if TIAN_GAN.index(year_gan) % 2 == 0 else "阴"
    direction = "forward" if (yy == "阳" and gender == "male") or (yy == "阴" and gender == "female") else "backward"
    start_age = ju_num * 10 - 8
    periods = []
    for i in range(12):
        age_start = start_age + i * 10
        age_end = age_start + 9
        periods.append({"age_range": f"{age_start}-{age_end}", "start_age": age_start})
    return {"start_age": start_age, "direction": direction, "periods": periods}


def calculate_ziwei(input_data: dict[str, Any]) -> dict[str, Any]:
    """紫微斗数排盘计算"""
    bd = input_data["birth_datetime"]
    parts = bd.replace("/", "-").split()
    date_parts = parts[0].split("-")
    year = int(date_parts[0])
    month = int(date_parts[1])

    time_str = parts[1] if len(parts) > 1 else "12:00"
    time_parts = time_str.split(":")
    hour = int(time_parts[0])
    minute = int(time_parts[1]) if len(time_parts) > 1 else 0

    gender = input_data.get("gender", "male")

    year_gz = _get_year_gan_zhi(year)
    year_gan = year_gz[0]
    month_zhi = _get_month_zhi(month)
    hour_zhi = _get_hour_zhi(hour, minute)

    ming_gong_idx = _determine_ming_gong(month_zhi, hour_zhi)
    shen_gong_idx = _determine_shen_gong(month_zhi, hour_zhi)

    ming_zhi = DI_ZHI[ming_gong_idx]
    wuxing_ju = _determine_wuxing_ju(ming_zhi)

    palaces = _place_main_stars(ming_gong_idx, wuxing_ju)
    sihua = _apply_sihua(year_gan, palaces)
    daxian = _determine_daxian(wuxing_ju, gender, year_gan)

    palace_info = []
    for i in range(12):
        name = PALACE_NAMES[i]
        palace_info.append({
            "name": name,
            "palace_idx": i,
            "stars": palaces.get(i, []),
            "is_ming": i == ming_gong_idx,
            "is_shen": i == shen_gong_idx,
            "sanfang": SANFANG_SIZHENG.get(name, {}),
        })

    return {
        "year_gan_zhi": year_gz,
        "month_zhi": month_zhi,
        "hour_zhi": hour_zhi,
        "ming_gong": PALACE_NAMES[ming_gong_idx],
        "shen_gong": PALACE_NAMES[shen_gong_idx],
        "ming_gong_zhi": DI_ZHI[ming_gong_idx],
        "wuxing_ju": wuxing_ju,
        "sihua": sihua,
        "daxian": daxian,
        "palaces": palace_info,
    }
