"""六爻排盘引擎 — 时间起卦"""

from __future__ import annotations

from datetime import datetime
from typing import Any

BAGUA_NAMES = ["坤", "震", "坎", "兑", "艮", "离", "巽", "乾"]
TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
LIUSHEN_ORDER = ["青龙", "朱雀", "勾陈", "螣蛇", "白虎", "玄武"]


def _hour_zhi(dt: datetime) -> int:
    return (dt.hour + 1) // 2 % 12


def _day_gan_idx(dt: datetime) -> int:
    base = datetime(2000, 1, 7)
    return (dt.date() - base.date()).days % 10


def calculate_liuyao(input_data: dict[str, Any]) -> dict[str, Any]:
    birth_str = input_data.get("birth_datetime", "")
    dt = datetime.strptime(birth_str, "%Y-%m-%d %H:%M")

    year_zhi_num = (dt.year - 4) % 12 + 1
    month, day = dt.month, dt.day
    hour_zhi_num = _hour_zhi(dt)

    shang_raw = (year_zhi_num + month + day) % 8
    shang_idx = (shang_raw if shang_raw != 0 else 8) - 1

    xia_raw = (year_zhi_num + month + day + hour_zhi_num) % 8
    xia_idx = (xia_raw if xia_raw != 0 else 8) - 1

    dong_yao_raw = (year_zhi_num + month + day + hour_zhi_num) % 6
    dong_yao = dong_yao_raw if dong_yao_raw != 0 else 6

    shang_name = BAGUA_NAMES[shang_idx]
    xia_name = BAGUA_NAMES[xia_idx]

    yao_list = []
    for i in range(1, 7):
        gua_name = xia_name if i <= 3 else shang_name
        yao_list.append({
            "yao_idx": i,
            "yin_yang": "阳" if i % 2 == 1 else "阴",
            "is_dong": i == dong_yao,
            "is_shi": i == dong_yao,
            "is_ying": i == ((dong_yao + 3 - 1) % 6 + 1),
            "gua_name": gua_name,
        })

    gan_idx = _day_gan_idx(dt)
    liushen = [LIUSHEN_ORDER[(gan_idx + i) % 6] for i in range(6)]

    return {
        "shang_gua": shang_name, "xia_gua": xia_name,
        "dong_yao": dong_yao, "shi_yao": dong_yao,
        "yao_list": yao_list, "liushen": liushen,
        "year_zhi_num": year_zhi_num, "month": month,
        "day": day, "hour_zhi_num": hour_zhi_num,
    }
