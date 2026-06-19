"""报告导出 + MCP 服务集成测试"""

import json
import pytest
from fastapi.testclient import TestClient

from xuanxue.core.registry import registry
from xuanxue.export.report import (
    Report, ReportSection,
    build_report, to_markdown, to_json, to_text,
    render_pillar_table, render_wuxing_bar, render_ziwei_palaces,
    render_dayun_table, render_chenggu, render_synthesis,
)

# ── 报告渲染测试 ──────────────────────────────────────────────


class TestReportRendering:
    """测试各模块的 Markdown 渲染"""

    def test_render_pillar_table(self):
        bazi = {
            "pillars": {"year": "甲子", "month": "丙寅", "day": "庚午", "hour": "戊子"},
            "shishen": {"year": "偏财", "month": "食神", "day": "日主", "hour": "偏印"},
            "cang_gan": {"year": ["癸"], "month": ["甲", "丙", "戊"], "day": ["丁", "己"], "hour": ["癸"]},
        }
        result = render_pillar_table(bazi)
        assert "甲" in result
        assert "庚" in result
        assert "年柱" in result
        assert "日柱" in result

    def test_render_wuxing_bar(self):
        wuxing = {"金": 2, "木": 3, "水": 1, "火": 4, "土": 2}
        result = render_wuxing_bar(wuxing)
        assert "金" in result
        assert "█" in result

    def test_render_ziwei_palaces_empty(self):
        assert render_ziwei_palaces({}) == "*（未排盘）*"

    def test_render_ziwei_palaces_with_data(self):
        ziwei = {
            "palaces": [
                {"name": "命宫", "stars": ["紫微", "天府"]},
                {"name": "兄弟", "stars": []},
            ],
            "sihua": {"禄": "太阳@田宅", "权": "武曲@命宫"},
        }
        result = render_ziwei_palaces(ziwei)
        assert "命宫" in result
        assert "紫微" in result
        assert "权" in result

    def test_render_dayun_table_empty(self):
        assert render_dayun_table({}) == "*（无法排列大运）*"

    def test_render_dayun_table_with_data(self):
        bazi = {"dayun": ["己卯", "庚辰", "辛巳"], "dayun_direction": "顺排"}
        result = render_dayun_table(bazi)
        assert "己卯" in result
        assert "顺排" in result

    def test_render_chenggu(self):
        chenggu = {"total_display": "三两八钱", "grade": "骨重适中", "verse": "一生骨肉最高清..."}
        result = render_chenggu(chenggu)
        assert "三两八钱" in result

    def test_render_synthesis(self):
        synthesis = {
            "final_verdict": "命局平和",
            "runnable_methods": ["bazi", "ziwei"],
            "blocked_methods": ["qimen"],
            "dimension_verdicts": [
                {"dimension": "性格", "best_method": "八字", "confidence": "高", "consensus": "稳重踏实"},
            ],
        }
        result = render_synthesis(synthesis)
        assert "命局平和" in result
        assert "八字" in result


# ── 报告构建测试 ──────────────────────────────────────────────


class TestBuildReport:
    """测试报告构建"""

    def test_build_minimal_report(self):
        report = build_report("张三", {"gender": "male"}, {})
        assert report.name == "张三"
        assert len(report.sections) == 1

    def test_build_full_report(self):
        method_results = {
            "bazi": {
                "pillars": {"year": "甲子", "month": "丙寅", "day": "庚午", "hour": "戊子"},
                "shishen": {"year": "偏财", "month": "食神", "day": "日主", "hour": "偏印"},
                "wuxing": {"金": 2, "木": 3, "水": 1, "火": 4, "土": 2},
                "dayun": ["己卯", "庚辰"],
                "cang_gan": {"year": ["癸"], "month": ["甲"], "day": ["丁"], "hour": ["癸"]},
            },
            "ziwei": {
                "palaces": [{"name": "命宫", "stars": ["紫微"]}],
                "ming_gong": "迁移",
                "shen_gong": "福德",
                "wuxing_ju": "水二局",
            },
            "chenggu": {"total_display": "三两八钱", "grade": "骨重适中", "verse": "..."},
        }
        synthesis = {
            "final_verdict": "命局平和",
            "runnable_methods": ["bazi", "ziwei", "chenggu"],
            "blocked_methods": [],
            "dimension_verdicts": [],
        }
        report = build_report("李四", {"gender": "female"}, method_results, synthesis)
        assert len(report.sections) == 5

    def test_to_markdown(self):
        report = build_report("王五", {"gender": "male"}, {})
        md = to_markdown(report)
        assert "王五" in md
        assert "仅供参考" in md

    def test_to_json(self):
        report = build_report("赵六", {"gender": "male"}, {})
        data = json.loads(to_json(report))
        assert data["name"] == "赵六"

    def test_to_text(self):
        report = build_report("孙七", {"gender": "female"}, {})
        text = to_text(report)
        assert "孙七" in text
        assert "**" not in text


# ── HTTP API 测试 ──────────────────────────────────────────────


class TestServerAPI:
    """测试 FastAPI 服务端点"""

    @pytest.fixture
    def client(self):
        from xuanxue.server import app
        return TestClient(app)

    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_list_methods(self, client):
        resp = client.get("/methods")
        assert resp.status_code == 200
        names = [m["name"] for m in resp.json()]
        assert "bazi" in names
        assert "ziwei" in names
        assert "qimen" in names
        assert "chenggu" in names

    def test_analyze_full(self, client):
        resp = client.post("/analyze", json={
            "name": "测试用户",
            "gender": "male",
            "birth_datetime": "1990-05-15 15:00",
            "birthplace": "北京市",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "测试用户"
        assert "report_markdown" in data
        assert len(data["methods_used"]) > 0

    def test_analyze_with_methods(self, client):
        resp = client.post("/analyze", json={
            "name": "测试",
            "gender": "female",
            "birth_datetime": "1988-12-25 08:30",
            "methods": ["bazi", "chenggu"],
        })
        assert resp.status_code == 200
        used = [m["name"] for m in resp.json()["methods_used"]]
        assert "bazi" in used
        assert "chenggu" in used

    def test_calculate_single_bazi(self, client):
        resp = client.post("/calculate/bazi", json={
            "name": "测试", "gender": "male", "birth_datetime": "1990-05-15 15:00",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["method"] == "bazi"
        assert "facts" in data

    def test_calculate_unknown_method(self, client):
        resp = client.post("/calculate/unknown", json={
            "name": "测试", "gender": "male", "birth_datetime": "1990-05-15 15:00",
        })
        assert resp.status_code == 404
