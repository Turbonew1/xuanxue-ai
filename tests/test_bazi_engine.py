"""八字引擎单元测试"""

from xuanxue.calculators.bazi_engine import (
    calculate_bazi,
    TIAN_GAN,
    DI_ZHI,
    SHISHEN_TABLE,
    CANG_GAN,
    WUXING_OF_GAN,
)


class TestBasicLookup:
    """基础数据表完整性测试"""

    def test_tian_gan_has_10_elements(self):
        assert len(TIAN_GAN) == 10

    def test_di_zhi_has_12_elements(self):
        assert len(DI_ZHI) == 12

    def test_shishen_table_covers_all_gan_pairs(self):
        for gan in TIAN_GAN:
            for other in TIAN_GAN:
                assert (gan, other) in SHISHEN_TABLE

    def test_cang_gan_covers_all_zhi(self):
        for zhi in DI_ZHI:
            assert zhi in CANG_GAN
            assert len(CANG_GAN[zhi]) >= 1

    def test_wuxing_of_gan_covers_all(self):
        for gan in TIAN_GAN:
            assert gan in WUXING_OF_GAN
            assert WUXING_OF_GAN[gan] in ("木", "火", "土", "金", "水")


class TestShishen:
    """十神计算测试"""

    def test_same_element_same_yinyang_is_bijian(self):
        assert SHISHEN_TABLE[("甲", "甲")] == "比肩"
        assert SHISHEN_TABLE[("乙", "乙")] == "比肩"

    def test_same_element_different_yinyang_is_jiecai(self):
        assert SHISHEN_TABLE[("甲", "乙")] == "劫财"
        assert SHISHEN_TABLE[("乙", "甲")] == "劫财"

    def test_me_generate_same_yinyang_is_shishen(self):
        assert SHISHEN_TABLE[("甲", "丙")] == "食神"

    def test_me_generate_different_yinyang_is_shangguan(self):
        assert SHISHEN_TABLE[("甲", "丁")] == "伤官"

    def test_me_ko_same_yinyang_is_piancai(self):
        assert SHISHEN_TABLE[("甲", "戊")] == "偏财"

    def test_me_ko_different_yinyang_is_zhengcai(self):
        assert SHISHEN_TABLE[("甲", "己")] == "正财"

    def test_ko_me_same_yinyang_is_qisha(self):
        assert SHISHEN_TABLE[("甲", "庚")] == "七杀"

    def test_ko_me_different_yinyang_is_zhengguan(self):
        assert SHISHEN_TABLE[("甲", "辛")] == "正官"

    def test_me_generate_same_yinyang_is_pianyin(self):
        assert SHISHEN_TABLE[("甲", "壬")] == "偏印"

    def test_me_generate_different_yinyang_is_zhengyin(self):
        assert SHISHEN_TABLE[("甲", "癸")] == "正印"


class TestCangGan:
    """藏干测试"""

    def test_zi_has_gangui(self):
        assert CANG_GAN["子"] == ["癸"]

    def test_yin_has_jia_bing_wu(self):
        assert CANG_GAN["寅"] == ["甲", "丙", "戊"]

    def test_hai_has_renjia(self):
        assert CANG_GAN["亥"] == ["壬", "甲"]

    def test_all_zhi_have_cang_gan(self):
        for zhi in DI_ZHI:
            assert len(CANG_GAN[zhi]) >= 1


class TestCalculateBazi:
    """八字排盘集成测试"""

    def test_basic_chart(self):
        result = calculate_bazi({
            "birth_datetime": "1990-05-15 14:30",
            "gender": "male",
        })
        assert "pillars" in result
        assert len(result["pillars"]) == 4
        assert all(k in result["pillars"] for k in ("year", "month", "day", "hour"))
        for gz in result["pillars"].values():
            assert len(gz) == 2
            assert gz[0] in TIAN_GAN
            assert gz[1] in DI_ZHI

    def test_shishen_present(self):
        result = calculate_bazi({
            "birth_datetime": "1990-05-15 14:30",
            "gender": "male",
        })
        assert "shishen" in result
        assert result["shishen"]["day"] == "日主"

    def test_wuxing_counts(self):
        result = calculate_bazi({
            "birth_datetime": "1990-05-15 14:30",
            "gender": "male",
        })
        assert "wuxing" in result
        total = sum(result["wuxing"].values())
        assert total >= 12

    def test_dayun_present(self):
        result = calculate_bazi({
            "birth_datetime": "1990-05-15 14:30",
            "gender": "male",
        })
        assert "dayun" in result
        assert len(result["dayun"]) == 8
        assert result["dayun_direction"] in ("顺排", "逆排")

    def test_night_hour(self):
        result = calculate_bazi({
            "birth_datetime": "1990-05-15 23:30",
            "gender": "male",
        })
        assert result["pillars"]["hour"][1] == "子"

    def test_different_gender_different_dayun(self):
        male = calculate_bazi({"birth_datetime": "1990-05-15 14:30", "gender": "male"})
        female = calculate_bazi({"birth_datetime": "1990-05-15 14:30", "gender": "female"})
        assert male["dayun"] != female["dayun"]
