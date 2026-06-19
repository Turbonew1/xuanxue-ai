"""新计算器测试 — 数字命理/梅花/六爻/六壬/金口诀/西方/吠陀"""

import pytest
from xuanxue.calculators.numerology_engine import calculate_numerology, get_strokes
from xuanxue.calculators.meihua_engine import calculate_meihua
from xuanxue.calculators.liuyao_engine import calculate_liuyao
from xuanxue.calculators.liuren_engine import calculate_liuren
from xuanxue.calculators.jinkou_engine import calculate_jinkou
from xuanxue.calculators.western_engine import calculate_western
from xuanxue.calculators.vedic_engine import calculate_vedic

BASE_INPUT = {"birth_datetime": "1990-05-15 15:00", "gender": "male", "name": "张三"}


class TestNumerology:
    def test_basic(self):
        r = calculate_numerology(BASE_INPUT)
        assert "life_number" in r
        assert 1 <= r["life_number"] <= 9
        assert r["name"] == "张三"

    def test_strokes(self):
        s = get_strokes("张三")
        assert len(s) == 2
        assert all(isinstance(x, int) for x in s)

    def test_grids(self):
        r = calculate_numerology(BASE_INPUT)
        assert all(k in r for k in ["tian_ge", "ren_ge", "di_ge", "wai_ge", "total_grid"])


class TestMeihua:
    def test_basic(self):
        r = calculate_meihua(BASE_INPUT)
        assert "ben_gua" in r
        assert 1 <= r["dong_yao"] <= 6
        assert "ti_yong_relation" in r


class TestLiuyao:
    def test_basic(self):
        r = calculate_liuyao(BASE_INPUT)
        assert len(r["yao_list"]) == 6
        assert len(r["liushen"]) == 6

    def test_yao_structure(self):
        r = calculate_liuyao(BASE_INPUT)
        for yao in r["yao_list"]:
            assert "yao_idx" in yao
            assert "yin_yang" in yao


class TestLiuren:
    def test_basic(self):
        r = calculate_liuren(BASE_INPUT)
        assert len(r["tian_pan"]) == 12
        assert "si_ke" in r


class TestJinkou:
    def test_basic(self):
        r = calculate_jinkou(BASE_INPUT)
        assert all(k in r for k in ["di_fen", "yue_jiang", "gui_shen", "ren_yuan"])


class TestWestern:
    def test_basic(self):
        r = calculate_western(BASE_INPUT)
        assert all(k in r for k in ["sun_sign", "moon_sign", "rising_sign"])
        valid = {"白羊座", "金牛座", "双子座", "巨蟹座", "狮子座", "处女座",
                 "天秤座", "天蝎座", "射手座", "摩羯座", "水瓶座", "双鱼座"}
        assert r["sun_sign"] in valid


class TestVedic:
    def test_basic(self):
        r = calculate_vedic(BASE_INPUT)
        assert "nakshatra" in r
        assert "tithi" in r


class TestRegistry:
    def test_all_registered(self):
        from xuanxue.core.registry import registry
        import xuanxue.core.methods  # noqa: F401
        names = {e.name for e in registry.list_all()}
        expected = {"bazi", "ziwei", "qimen", "chenggu", "numerology",
                    "meihua", "liuyao", "liuren", "jinkou", "western", "vedic"}
        assert expected.issubset(names)

    def test_all_runnable(self):
        from xuanxue.core.registry import registry, MethodStatus
        import xuanxue.core.methods  # noqa: F401
        for entry in registry.list_all():
            status = registry.check_status(entry.name, BASE_INPUT)
            assert status == MethodStatus.RUNNABLE, f"{entry.name}: {status}"
