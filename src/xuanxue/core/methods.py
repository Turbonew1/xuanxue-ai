"""方法注册模块 — 将所有计算引擎注册到注册表"""

from xuanxue.core.registry import MethodEntry, MethodRegistry, registry
from xuanxue.calculators.bazi_engine import calculate_bazi
from xuanxue.calculators.chenggu_engine import calculate_chenggu
from xuanxue.calculators.ziwei_engine import calculate_ziwei
from xuanxue.calculators.qimen_engine import calculate_qimen
from xuanxue.calculators.numerology_engine import calculate_numerology
from xuanxue.calculators.meihua_engine import calculate_meihua
from xuanxue.calculators.liuyao_engine import calculate_liuyao
from xuanxue.calculators.liuren_engine import calculate_liuren
from xuanxue.calculators.jinkou_engine import calculate_jinkou
from xuanxue.calculators.western_engine import calculate_western
from xuanxue.calculators.vedic_engine import calculate_vedic


def register_all(reg: MethodRegistry = registry) -> None:
    """注册所有命理方法到注册表"""
    reg.register(MethodEntry(
        name="bazi", display_name="八字命理",
        description="四柱八字排盘与命理分析",
        calculator=calculate_bazi, required_fields=["birth_datetime", "gender"],
    ))
    reg.register(MethodEntry(
        name="ziwei", display_name="紫微斗数",
        description="紫微斗数排盘与宫位分析",
        calculator=calculate_ziwei, required_fields=["birth_datetime", "gender"],
    ))
    reg.register(MethodEntry(
        name="qimen", display_name="奇门遁甲",
        description="时家奇门遁甲排盘与格局分析",
        calculator=calculate_qimen, required_fields=["birth_datetime"],
    ))
    reg.register(MethodEntry(
        name="chenggu", display_name="称骨算命",
        description="袁天罡称骨算命法",
        calculator=calculate_chenggu, required_fields=["birth_datetime"],
    ))
    reg.register(MethodEntry(
        name="numerology", display_name="数字命理",
        description="五格剖象法与生命数分析",
        calculator=calculate_numerology, required_fields=["birth_datetime", "name"],
    ))
    reg.register(MethodEntry(
        name="meihua", display_name="梅花易数",
        description="时间起卦梅花易数分析",
        calculator=calculate_meihua, required_fields=["birth_datetime"],
    ))
    reg.register(MethodEntry(
        name="liuyao", display_name="六爻排盘",
        description="时间六爻排盘分析",
        calculator=calculate_liuyao, required_fields=["birth_datetime"],
    ))
    reg.register(MethodEntry(
        name="liuren", display_name="大六壬",
        description="月将加时大六壬排盘",
        calculator=calculate_liuren, required_fields=["birth_datetime"],
    ))
    reg.register(MethodEntry(
        name="jinkou", display_name="金口诀",
        description="四柱金口诀排盘",
        calculator=calculate_jinkou, required_fields=["birth_datetime"],
    ))
    reg.register(MethodEntry(
        name="western", display_name="西方占星",
        description="太阳/月亮/上升星座分析",
        calculator=calculate_western, required_fields=["birth_datetime"],
    ))
    reg.register(MethodEntry(
        name="vedic", display_name="吠陀占星",
        description="恒星黄道与Nakshatra分析",
        calculator=calculate_vedic, required_fields=["birth_datetime"],
    ))


# 模块导入时自动注册
register_all()
