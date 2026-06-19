"""Phase 2 引擎测试：称骨、紫微、奇门"""

from xuanxue.calculators.chenggu_engine import calculate_chenggu, VERSE_TABLE
from xuanxue.calculators.ziwei_engine import calculate_ziwei, PALACE_NAMES, SIHUA_TABLE
from xuanxue.calculators.qimen_engine import calculate_qimen, JIUGONG_NAMES
from xuanxue.core.registry import registry, MethodStatus


class TestChenggu:
    def test_basic_calculation(self):
        result = calculate_chenggu({
            "birth_datetime": "1990-05-15 14:30",
            "gender": "male",
        })
        assert "total_qian" in result
        assert "total_display" in result
        assert "grade" in result
        assert "verse" in result
        assert result["grade"] in ("凶", "中吉", "吉", "大吉")

    def test_weights_sum_correct(self):
        result = calculate_chenggu({
            "birth_datetime": "1990-05-15 14:30",
            "gender": "male",
        })
        w = result["weights"]
        assert result["total_qian"] == w["year"] + w["month"] + w["day"] + w["hour"]

    def test_night_hour_rollover(self):
        r1 = calculate_chenggu({"birth_datetime": "1990-05-15 22:00", "gender": "male"})
        r2 = calculate_chenggu({"birth_datetime": "1990-05-15 23:30", "gender": "male"})
        assert r1["weights"]["day"] != r2["weights"]["day"] or r1["total_qian"] != r2["total_qian"]

    def test_verse_table_not_empty(self):
        assert len(VERSE_TABLE) >= 50


class TestZiwei:
    def test_basic_chart(self):
        result = calculate_ziwei({
            "birth_datetime": "1990-05-15 14:30",
            "gender": "male",
        })
        assert "palaces" in result
        assert len(result["palaces"]) == 12

    def test_palace_names(self):
        result = calculate_ziwei({
            "birth_datetime": "1990-05-15 14:30",
            "gender": "male",
        })
        for p in result["palaces"]:
            assert p["name"] in PALACE_NAMES

    def test_ming_gong_present(self):
        result = calculate_ziwei({
            "birth_datetime": "1990-05-15 14:30",
            "gender": "male",
        })
        assert result["ming_gong"] in PALACE_NAMES
        assert result["shen_gong"] in PALACE_NAMES

    def test_wuxing_ju(self):
        result = calculate_ziwei({
            "birth_datetime": "1990-05-15 14:30",
            "gender": "male",
        })
        assert "局" in result["wuxing_ju"]

    def test_sihua(self):
        result = calculate_ziwei({
            "birth_datetime": "1990-05-15 14:30",
            "gender": "male",
        })
        assert "sihua" in result
        for key in ("禄", "权", "科", "忌"):
            assert key in result["sihua"]

    def test_daxian(self):
        result = calculate_ziwei({
            "birth_datetime": "1990-05-15 14:30",
            "gender": "male",
        })
        assert "daxian" in result
        assert result["daxian"]["direction"] in ("forward", "backward")
        assert len(result["daxian"]["periods"]) == 12

    def test_sihua_table_complete(self):
        for gan in "甲乙丙丁戊己庚辛壬癸":
            assert gan in SIHUA_TABLE
            assert len(SIHUA_TABLE[gan]) == 4


class TestQimen:
    def test_basic_chart(self):
        result = calculate_qimen({
            "birth_datetime": "2024-06-15 10:30",
            "gender": "male",
        })
        assert "palaces" in result
        assert len(result["palaces"]) == 9

    def test_palace_names(self):
        result = calculate_qimen({
            "birth_datetime": "2024-06-15 10:30",
            "gender": "male",
        })
        for p in result["palaces"]:
            assert p["name"] in JIUGONG_NAMES

    def test_dun_type(self):
        result = calculate_qimen({
            "birth_datetime": "2024-06-15 10:30",
            "gender": "male",
        })
        assert result["dun_type"] in ("阳遁", "阴遁")

    def test_ju_range(self):
        result = calculate_qimen({
            "birth_datetime": "2024-06-15 10:30",
            "gender": "male",
        })
        assert 1 <= result["ju"] <= 9

    def test_xunshou(self):
        result = calculate_qimen({
            "birth_datetime": "2024-06-15 10:30",
            "gender": "male",
        })
        assert result["xunshou"].startswith("甲")
        assert result["hidden_gan"] in "戊己庚辛壬癸"

    def test_ganzhi_present(self):
        result = calculate_qimen({
            "birth_datetime": "2024-06-15 10:30",
            "gender": "male",
        })
        assert all(k in result["ganzhi"] for k in ("year", "month", "day", "hour"))


class TestRegistry:
    def test_all_methods_registered(self):
        from xuanxue.core.methods import register_all
        register_all(registry)
        names = [e.name for e in registry.list_all()]
        assert "bazi" in names
        assert "chenggu" in names
        assert "ziwei" in names
        assert "qimen" in names

    def test_bazi_runnable(self):
        status = registry.check_status("bazi", {
            "birth_datetime": "1990-05-15 14:30",
            "gender": "male",
        })
        assert status == MethodStatus.RUNNABLE

    def test_chenggu_runnable_without_gender(self):
        status = registry.check_status("chenggu", {
            "birth_datetime": "1990-05-15 14:30",
        })
        assert status == MethodStatus.RUNNABLE
