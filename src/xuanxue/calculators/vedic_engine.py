"""吠陀占星引擎 — 恒星黄道 + Nakshatra"""

from __future__ import annotations

from datetime import datetime
from typing import Any

NAKSHATRAS = [
    ("Ashwini", "马头"), ("Bharani", "承载"), ("Krittika", "剃刀"),
    ("Rohini", "红"), ("Mrigashira", "鹿头"), ("Ardra", "星"),
    ("Punarvasu", "弓"), ("Pushya", "莲花"), ("Ashlesha", "蛇"),
    ("Magha", "王座"), ("Purva Phalguni", "床"), ("Uttara Phalguni", "床"),
    ("Hasta", "手"), ("Chitra", "珠"), ("Swati", "珊瑚"),
    ("Vishakha", "门"), ("Anuradha", "莲"), ("Jyeshtha", "伞"),
    ("Mula", "根"), ("Purva Ashadha", "象牙"), ("Uttara Ashadha", "象牙"),
    ("Shravana", "耳"), ("Dhanishta", "鼓"), ("Shatabhisha", "百"),
    ("Purva Bhadrapada", "剑"), ("Uttara Bhadrapada", "双人"), ("Revati", "鱼"),
]

TITHIS = [
    "Shukla Pratipada", "Shukla Dwitiya", "Shukla Tritiya", "Shukla Chaturthi",
    "Shukla Panchami", "Shukla Shashthi", "Shukla Saptami", "Shukla Ashtami",
    "Shukla Navami", "Shukla Dashami", "Shukla Ekadashi", "Shukla Dwadashi",
    "Shukla Trayodashi", "Shukla Chaturdashi", "Purnima",
    "Krishna Pratipada", "Krishna Dwitiya", "Krishna Tritiya", "Krishna Chaturthi",
    "Krishna Panchami", "Krishna Shashthi", "Krishna Saptami", "Krishna Ashtami",
    "Krishna Navami", "Krishna Dashami", "Krishna Ekadashi", "Krishna Dwadashi",
    "Krishna Trayodashi", "Krishna Chaturdashi", "Amavasya",
]

ZODIAC = ["白羊", "金牛", "双子", "巨蟹", "狮子", "处女",
          "天秤", "天蝎", "射手", "摩羯", "水瓶", "双鱼"]


def calculate_vedic(input_data: dict[str, Any]) -> dict[str, Any]:
    birth_str = input_data.get("birth_datetime", "")
    dt = datetime.strptime(birth_str, "%Y-%m-%d %H:%M")

    total_days = (dt.year - 1900) * 365 + dt.month * 30 + dt.day
    nak_idx = total_days % 27
    name, symbol = NAKSHATRAS[nak_idx]
    tithi_idx = total_days % 30

    sun_sign_idx = ((dt.month - 1) * 31 + dt.day) % 12
    sidereal_sun = ZODIAC[(sun_sign_idx + 1) % 12]

    return {
        "sidereal_correction_deg": -23.85,
        "sun_sign_sidereal": sidereal_sun,
        "nakshatra": {"name": name, "symbol": symbol, "index": nak_idx + 1},
        "tithi": TITHIS[tithi_idx],
    }
