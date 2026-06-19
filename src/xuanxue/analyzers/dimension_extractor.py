"""确定性维度信号提取器 — 从排盘数据直接提取六维度信号（无需 LLM）"""

from __future__ import annotations

from typing import Any


def extract_dimensions(method: str, facts: dict[str, Any]) -> dict[str, str]:
    """从方法的 facts 中提取六维度信号"""
    extractor = _EXTRACTORS.get(method, _default_extract)
    return extractor(facts)


def _default_extract(facts: dict[str, Any]) -> dict[str, str]:
    return {}


def _extract_bazi(facts: dict[str, Any]) -> dict[str, str]:
    wuxing = facts.get("wuxing", {})
    shishen = facts.get("shishen", {})
    dims: dict[str, str] = {}

    wuxing_map = {"金": "果断刚毅", "木": "仁慈正直", "水": "智慧灵活", "火": "热情急躁", "土": "稳重务实"}
    ri_gan_wx = facts.get("ri_gan_wuxing", "")
    if ri_gan_wx in wuxing_map:
        dims["personality"] = wuxing_map[ri_gan_wx]

    if "偏官" in shishen.values() or "正官" in shishen.values():
        dims["career"] = "适合管理或公职"
    elif "食神" in shishen.values() or "伤官" in shishen.values():
        dims["career"] = "适合创意或技术"
    elif "偏财" in shishen.values() or "正财" in shishen.values():
        dims["career"] = "适合经商或金融"

    if "偏财" in shishen.values() or "正财" in shishen.values():
        dims["wealth"] = "财星透出，有求财机会"

    if "正官" in shishen.values():
        dims["relationship"] = "重规矩，感情稳定"
    elif "七杀" in shishen.values():
        dims["relationship"] = "个性强，需包容"

    if wuxing:
        max_wx = max(wuxing, key=wuxing.get)
        min_wx = min(wuxing, key=wuxing.get)
        if wuxing.get(max_wx, 0) - wuxing.get(min_wx, 0) >= 4:
            dims["health"] = f"{max_wx}旺{min_wx}弱，注意五行平衡"

    dayun = facts.get("dayun", [])
    if dayun:
        dims["timing"] = f"大运{len(dayun)}步，{facts.get('dayun_direction', '')}排"

    return dims


def _extract_ziwei(facts: dict[str, Any]) -> dict[str, str]:
    dims: dict[str, str] = {}
    palaces = facts.get("palaces", [])
    sihua = facts.get("sihua", {})

    star_map = {
        "紫微": "尊贵有主见", "天机": "聪明善变", "太阳": "热情大方",
        "武曲": "果断务实", "天同": "温和随性", "廉贞": "多才多虑",
        "天府": "稳重保守", "太阴": "细腻内敛", "贪狼": "多才好动",
        "巨门": "口才好但多疑", "天相": "正直助人", "天梁": "稳重有靠山",
        "七杀": "刚强有魄力", "破军": "开创有冲劲",
    }
    for p in palaces:
        if p.get("is_ming"):
            stars = p.get("stars", [])
            if stars:
                dims["personality"] = star_map.get(stars[0], f"{stars[0]}特质")
            break

    for p in palaces:
        if p.get("name") in ("官禄", "事业"):
            stars = p.get("stars", [])
            if stars:
                dims["career"] = f"官禄宫{'、'.join(stars)}，事业有方向"
            break

    for p in palaces:
        if p.get("name") == "财帛":
            stars = p.get("stars", [])
            if stars:
                dims["wealth"] = f"财帛宫{'、'.join(stars)}"
            break

    if sihua:
        dims["timing"] = "四化：" + "、".join(f"{k}→{v.split('@')[0]}" for k, v in sihua.items())

    return dims


def _extract_qimen(facts: dict[str, Any]) -> dict[str, str]:
    dims: dict[str, str] = {}
    palaces = facts.get("palaces", [])

    for p in palaces:
        if p.get("qi_yi"):
            dims["timing"] = f"值符落{p.get('name', '')}宫，时运关键"
            break

    for p in palaces:
        men = p.get("men", "")
        if men in ("开门", "休门", "生门"):
            dims["career"] = f"{men}主事，有利于事业"
            break

    return dims


def _extract_chenggu(facts: dict[str, Any]) -> dict[str, str]:
    dims: dict[str, str] = {}
    total = facts.get("total_qian", 0)
    grade = facts.get("grade", "")

    if grade:
        dims["personality"] = f"命评：{grade}"

    if total >= 50:
        dims["career"] = "骨重较高，福禄深厚"
        dims["wealth"] = "财运较佳"
    elif total >= 35:
        dims["career"] = "骨重适中，平顺之命"
    else:
        dims["career"] = "骨重偏轻，需自力更生"

    return dims


def _extract_numerology(facts: dict[str, Any]) -> dict[str, str]:
    dims: dict[str, str] = {}
    life_number = facts.get("life_number", 0)
    traits = {1: "独立领导", 2: "合作协调", 3: "创意表达", 4: "务实稳重",
              5: "变化自由", 6: "责任关怀", 7: "内省智慧", 8: "成就权力", 9: "理想奉献"}
    if 1 <= life_number <= 9:
        dims["personality"] = f"生命数{life_number}：{traits.get(life_number, '')}"
    total_grid = facts.get("total_grid", 0)
    if total_grid >= 30:
        dims["career"] = "总格较高，事业有成"
    return dims


def _extract_meihua(facts: dict[str, Any]) -> dict[str, str]:
    dims: dict[str, str] = {}
    relation = facts.get("ti_yong_relation", "")
    if relation:
        dims["personality"] = f"体用关系：{relation}"
    ti_gua = facts.get("ti_gua", "")
    if ti_gua:
        dims["timing"] = f"体卦{ti_gua}，主当前状态"
    return dims


_EXTRACTORS = {
    "bazi": _extract_bazi,
    "ziwei": _extract_ziwei,
    "qimen": _extract_qimen,
    "chenggu": _extract_chenggu,
    "numerology": _extract_numerology,
    "meihua": _extract_meihua,
}
