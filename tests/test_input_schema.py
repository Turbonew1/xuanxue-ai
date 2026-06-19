"""输入 Schema 单元测试"""

import pytest
from pydantic import ValidationError

from xuanxue.core.input_schema import (
    AnalysisRequest,
    Assertiveness,
    BirthInput,
    CalendarType,
    Gender,
    RenderConfig,
    StyleMode,
    YearWindow,
)


class TestBirthInput:
    def test_valid_solar_input(self):
        b = BirthInput(
            name="张三",
            gender=Gender.MALE,
            birth_datetime="1990-05-15 14:30",
        )
        assert b.name == "张三"
        assert b.calendar_type == CalendarType.SOLAR

    def test_valid_lunar_input(self):
        b = BirthInput(
            name="李四",
            gender=Gender.FEMALE,
            birth_datetime="1990-05-15",
            calendar_type=CalendarType.LUNAR,
        )
        assert b.calendar_type == CalendarType.LUNAR

    def test_invalid_datetime_format(self):
        with pytest.raises(ValidationError):
            BirthInput(
                name="王五",
                gender=Gender.MALE,
                birth_datetime="15/05/1990",
            )

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            BirthInput(
                name="",
                gender=Gender.MALE,
                birth_datetime="1990-05-15",
            )

    def test_to_dict(self):
        b = BirthInput(
            name="张三",
            gender=Gender.MALE,
            birth_datetime="1990-05-15 14:30",
        )
        d = b.to_dict()
        assert d["name"] == "张三"
        assert d["gender"] == "male"
        assert d["birth_datetime"] == "1990-05-15 14:30"


class TestRenderConfig:
    def test_default_config(self):
        rc = RenderConfig()
        assert rc.style_mode == StyleMode.CONSERVATIVE
        assert rc.assertiveness == Assertiveness.MEDIUM

    def test_from_user_hints_direct(self):
        rc = RenderConfig.from_user_hints(["直断", "详细分析"])
        assert rc.style_mode == StyleMode.DIRECT
        assert rc.assertiveness == Assertiveness.HIGH

    def test_from_user_hints_conservative(self):
        rc = RenderConfig.from_user_hints(["简单看看"])
        assert rc.style_mode == StyleMode.CONSERVATIVE


class TestYearWindow:
    def test_default_window(self):
        yw = YearWindow()
        assert yw.past == 2
        assert yw.future == 2


class TestAnalysisRequest:
    def test_full_request(self):
        req = AnalysisRequest(
            input=BirthInput(
                name="张三",
                gender=Gender.MALE,
                birth_datetime="1990-05-15 14:30",
            ),
            config=RenderConfig(style_mode=StyleMode.DIRECT),
            methods=["bazi", "ziwei"],
        )
        assert req.input.name == "张三"
        assert req.config.style_mode == StyleMode.DIRECT
        assert len(req.methods) == 2
