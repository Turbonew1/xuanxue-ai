"""报告导出 — 将排盘+综合分析结果渲染为 Markdown / JSON 报告"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


# ── 报告数据结构 ──────────────────────────────────────────────


@dataclass(frozen=True)
class ReportSection:
    """报告单节"""
    title: str
    content: str
    order: int


@dataclass(frozen=True)
class Report:
    """完整命理报告"""
    name: str
    birth_info: dict[str, Any]
    method_results: dict[str, Any]
    synthesis: dict[str, Any] | None
    sections: list[ReportSection] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "birth_info": self.birth_info,
            "method_results": self.method_results,
            "synthesis": self.synthesis,
            "sections": [asdict(s) for s in self.sections],
            "generated_at": self.generated_at,
        }


# ── Markdown 渲染 ──────────────────────────────────────────────


def render_pillar_table(bazi: dict) -> str:
    """渲染八字四柱表格（适配 bazi_engine 输出格式）"""
    pillars = bazi.get("pillars", {})
    shishen = bazi.get("shishen", {})

    header = "|      | 年柱 | 月柱 | 日柱 | 时柱 |"
    sep    = "|------|------|------|------|------|"

    # 天干：取每柱第一个字
    tg_cells = [pillars.get(p, "—")[0] if pillars.get(p, "") else "—" for p in ["year", "month", "day", "hour"]]
    # 地支：取每柱第二个字
    dz_cells = [pillars.get(p, "—")[1] if len(pillars.get(p, "")) > 1 else "—" for p in ["year", "month", "day", "hour"]]
    # 十神
    ss_cells = [shishen.get(p, "—") for p in ["year", "month", "day", "hour"]]

    rows = [
        f"| 天干 | {' | '.join(tg_cells)} |",
        f"| 地支 | {' | '.join(dz_cells)} |",
        f"| 十神 | {' | '.join(ss_cells)} |",
    ]

    # 藏干
    cang = bazi.get("cang_gan", {})
    cang_cells = [", ".join(cang.get(p, [])) or "—" for p in ["year", "month", "day", "hour"]]
    rows.append(f"| 藏干 | {' | '.join(cang_cells)} |")

    return "\n".join([header, sep] + rows)


def render_wuxing_bar(wuxing: dict) -> str:
    """渲染五行力量条（适配 bazi_engine 输出格式）"""
    mapping = {"金": "金", "木": "木", "水": "水", "火": "火", "土": "土"}
    lines = ["**五行力量分布：**", ""]
    for cn in mapping:
        count = wuxing.get(cn, 0)
        bar = "█" * count + "░" * max(0, 8 - count)
        lines.append(f"- {cn}：{bar}（{count}）")
    return "\n".join(lines)


def render_ziwei_palaces(ziwei: dict) -> str:
    """渲染紫微斗数十二宫（适配 ziwei_engine 输出格式）"""
    palaces = ziwei.get("palaces", [])
    if not palaces:
        return "*（未排盘）*"

    lines = ["| 宫位 | 主星 | 四化 |", "|------|------|------|"]
    sihua = ziwei.get("sihua", {})
    # 构建宫位→四化反向索引
    palace_sihua: dict[str, list[str]] = {}
    for shen, loc in sihua.items():
        palace_name = loc.split("@")[-1] if "@" in loc else ""
        palace_sihua.setdefault(palace_name, []).append(shen)

    for p in palaces:
        name = p.get("name", "")
        stars = ", ".join(p.get("stars", [])) or "—"
        sh = ", ".join(palace_sihua.get(name, [])) or "—"
        lines.append(f"| {name} | {stars} | {sh} |")
    return "\n".join(lines)


def render_dayun_table(bazi: dict) -> str:
    """渲染大运表格（适配 bazi_engine 输出格式）"""
    dayun = bazi.get("dayun", [])
    if not dayun:
        return "*（无法排列大运）*"

    direction = bazi.get("dayun_direction", "")
    lines = [f"**排列方向：** {direction}", ""]
    lines += ["| 序号 | 干支 |", "|------|------|"]
    for i, gz in enumerate(dayun, 1):
        lines.append(f"| {i} | {gz} |")
    return "\n".join(lines)


def render_chenggu(chenggu: dict) -> str:
    """渲染称骨结果"""
    total = chenggu.get("total_display", chenggu.get("total_qian", ""))
    grade = chenggu.get("grade", "")
    verse = chenggu.get("verse", "")
    return f"**称骨总重：** {total}\n\n**命评：** {grade}\n\n**批语：** {verse}"


def render_synthesis(synthesis: dict) -> str:
    """渲染综合分析结论"""
    lines = [
        "## 综合结论",
        "",
        f"**综合运势：** {synthesis.get('final_verdict', '')}",
        "",
        "### 各维度分析",
        "",
        "| 维度 | 最佳方法 | 共识度 | 信号 |",
        "|------|---------|--------|------|",
    ]
    for v in synthesis.get("dimension_verdicts", []):
        lines.append(f"| {v.get('dimension','')} | {v.get('best_method','')} | {v.get('confidence','')} | {v.get('consensus','')} |")

    lines.append("")
    runnable = synthesis.get("runnable_methods", [])
    blocked = synthesis.get("blocked_methods", [])
    lines.append(f"*参与方法：{', '.join(runnable)}*")
    if blocked:
        lines.append(f"*未参与方法：{', '.join(blocked)}*")

    return "\n".join(lines)


# ── 完整报告构建 ──────────────────────────────────────────────


def build_report(
    name: str,
    birth_info: dict[str, Any],
    method_results: dict[str, Any],
    synthesis: dict[str, Any] | None = None,
) -> Report:
    """构建完整报告"""
    sections: list[ReportSection] = []

    # 基本信息
    sections.append(ReportSection(
        title="基本信息",
        content=(
            f"- 姓名：{name}\n"
            f"- 性别：{birth_info.get('gender', '未知')}\n"
            f"- 出生时间：{birth_info.get('birth_datetime', '未知')}\n"
            f"- 出生地：{birth_info.get('birthplace', '未知')}"
        ),
        order=1,
    ))

    # 八字排盘
    if "bazi" in method_results:
        bazi = method_results["bazi"]
        content = "## 八字排盘\n\n" + render_pillar_table(bazi)
        content += "\n\n" + render_wuxing_bar(bazi.get("wuxing", {}))
        content += "\n\n## 大运排列\n\n" + render_dayun_table(bazi)
        sections.append(ReportSection(title="八字命理", content=content, order=2))

    # 紫微斗数
    if "ziwei" in method_results:
        ziwei = method_results["ziwei"]
        content = "## 紫微斗数排盘\n\n" + render_ziwei_palaces(ziwei)
        content += f"\n\n**命宫：** {ziwei.get('ming_gong', '—')}"
        content += f"\n\n**身宫：** {ziwei.get('shen_gong', '—')}"
        content += f"\n\n**五行局：** {ziwei.get('wuxing_ju', '—')}"
        sections.append(ReportSection(title="紫微斗数", content=content, order=3))

    # 奇门遁甲
    if "qimen" in method_results:
        qimen = method_results["qimen"]
        content = "## 奇门遁甲\n\n"
        content += f"**局数：** {qimen.get('ju', '—')}局 {qimen.get('dun_type', '')}\n\n"
        content += f"**旬首：** {qimen.get('xunshou', '—')}\n\n"
        palaces = qimen.get("palaces", [])
        if palaces:
            content += "| 宫位 | 值符 | 八门 | 九星 | 八神 |\n"
            content += "|------|------|------|------|------|\n"
            for p in palaces:
                content += f"| {p.get('name','')} | {p.get('qi_yi','')} | {p.get('men','')} | {p.get('xing','')} | {p.get('shen','')} |\n"
        sections.append(ReportSection(title="奇门遁甲", content=content, order=4))

    # 称骨
    if "chenggu" in method_results:
        content = "## 称骨算命\n\n" + render_chenggu(method_results["chenggu"])
        sections.append(ReportSection(title="称骨算命", content=content, order=5))

    # 综合分析
    if synthesis:
        sections.append(ReportSection(
            title="综合分析",
            content=render_synthesis(synthesis),
            order=6,
        ))

    return Report(
        name=name,
        birth_info=birth_info,
        method_results=method_results,
        synthesis=synthesis,
        sections=sections,
    )


# ── 格式输出 ──────────────────────────────────────────────────


def to_markdown(report: Report) -> str:
    """渲染为 Markdown"""
    parts = [
        f"# {report.name} — 命理综合分析报告",
        "",
        f"*生成时间：{report.generated_at}*",
        "",
    ]
    sorted_sections = sorted(report.sections, key=lambda s: s.order)
    for section in sorted_sections:
        parts.append(f"## {section.title}\n\n{section.content}\n")
    parts.append("---\n*命理分析仅供参考，人生在于自身的努力和选择。*")
    return "\n".join(parts)


def to_json(report: Report) -> str:
    """渲染为 JSON"""
    return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)


def to_text(report: Report) -> str:
    """渲染为纯文本（去除 Markdown 标记）"""
    md = to_markdown(report)
    text = md.replace("**", "").replace("## ", "").replace("# ", "")
    text = text.replace("|", " ").replace("---", "")
    lines = [line.strip() for line in text.split("\n")]
    cleaned = []
    prev_empty = False
    for line in lines:
        if not line:
            if not prev_empty:
                cleaned.append("")
            prev_empty = True
        else:
            cleaned.append(line)
            prev_empty = False
    return "\n".join(cleaned)
