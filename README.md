# 🔮 玄学命理 AI (Xuanxue AI)

> 综合玄学命理分析 Skill — 融合 **11 种命理方法** 的统一分析引擎

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-86%20passing-brightgreen.svg)](#测试)

[English](README_EN.md) | 中文

---

## ✨ 特性

- **11 种命理方法**：八字、紫微斗数、奇门遁甲、称骨、数字命理、梅花易数、六爻、大六壬、金口诀、西方占星、吠陀占星
- **确定性计算**：排盘引擎由 Python 实现，结果精确可复现
- **六维度交叉验证**：性格/事业/财运/关系/身心/阶段，多法验证
- **反幻觉设计**：LLM 只做解读和建议，不做排盘计算
- **详细报告**：包含破解方法、流年预测、吉祥配置

---

## 🚀 快速开始

### 方式一：pip 安装（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/Turbonew1/xuanxue-ai.git
cd xuanxue-ai

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# 或 .venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -e .

# 4. 验证安装
python -m xuanxue.core.cli methods
```

### 方式二：uv 安装（更快）

```bash
# 1. 安装 uv（如果没有）
pip install uv

# 2. 克隆仓库
git clone https://github.com/Turbonew1/xuanxue-ai.git
cd xuanxue-ai

# 3. 创建虚拟环境并安装
uv venv .venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# 4. 验证安装
python -m xuanxue.core.cli methods
```

### 方式三：Docker

```bash
# 1. 克隆仓库
git clone https://github.com/Turbonew1/xuanxue-ai.git
cd xuanxue-ai

# 2. 构建镜像
docker build -t xuanxue-ai .

# 3. 运行容器
docker run -p 8600:8600 xuanxue-ai

# 4. 验证（新终端）
curl http://localhost:8600/health
```

### 安装验证

```bash
# 查看所有支持的方法
python -m xuanxue.core.cli methods

# 输出示例：
#   bazi         八字命理       四柱八字排盘与命理分析
#   ziwei        紫微斗数       紫微斗数排盘与宫位分析
#   qimen        奇门遁甲       时家奇门遁甲排盘与格局分析
#   chenggu      称骨算命       袁天罡称骨算命法
#   numerology   数字命理       五格剖象法与生命数分析
#   meihua       梅花易数       时间起卦梅花易数分析
#   liuyao       六爻排盘       时间六爻排盘分析
#   liuren       大六壬        月将加时大六壬排盘
#   jinkou       金口诀        四柱金口诀排盘
#   western      西方占星       太阳/月亮/上升星座分析
#   vedic        吠陀占星       恒星黄道与Nakshatra分析
```

---

## 📊 支持的 11 种方法

| 方法 | 引擎 | 功能 | 需要信息 |
|------|------|------|---------|
| **八字命理** | `bazi_engine` | 四柱排盘、十神、藏干、五行、大运、格局、用神 | 出生时间、性别 |
| **紫微斗数** | `ziwei_engine` | 12宫、主星、四化、大限、流年 | 出生时间、性别 |
| **奇门遁甲** | `qimen_engine` | 9宫、八门、九星、八神、用神定位 | 出生时间 |
| **称骨算命** | `chenggu_engine` | 骨重计算、批语 | 出生时间 |
| **数字命理** | `numerology_engine` | 五格剖象法、生命数 | 姓名、出生时间 |
| **梅花易数** | `meihua_engine` | 时间起卦、体用生克、互卦变卦 | 出生时间 |
| **六爻排盘** | `liuyao_engine` | 六爻、世应、六神、纳甲 | 出生时间 |
| **大六壬** | `liuren_engine` | 月将加时、四课三传、天将 | 出生时间 |
| **金口诀** | `jinkou_engine` | 四柱起课、五行生克 | 出生时间 |
| **西方占星** | `western_engine` | 太阳/月亮/上升星座、四元素 | 出生时间 |
| **吠陀占星** | `vedic_engine` | 恒星黄道、Nakshatra、Tithi | 出生时间 |

---

## 🎯 使用方式

### 方式 1：CLI 命令行

```bash
# 综合分析（自动选择所有方法）
python -m xuanxue.core.cli analyze \
  --name "张三" \
  --gender male \
  --birth "1990-05-15 15:00" \
  --format markdown

# 指定方法
python -m xuanxue.core.cli analyze \
  --name "李四" \
  --gender female \
  --birth "1988-12-25 08:30" \
  --methods bazi ziwei chenggu \
  --format json

# 输出 JSON 格式
python -m xuanxue.core.cli analyze \
  --name "王五" \
  --gender male \
  --birth "1985-03-20 10:30" \
  --format json
```

### 方式 2：HTTP API

```bash
# 启动服务
python -m xuanxue.server

# 服务启动后，在另一个终端：
# 健康检查
curl http://localhost:8600/health

# 列出所有方法
curl http://localhost:8600/methods

# 综合分析
curl -X POST http://localhost:8600/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "name": "张三",
    "gender": "male",
    "birth_datetime": "1990-05-15 15:00",
    "birthplace": "北京市"
  }'

# 单方法排盘
curl -X POST http://localhost:8600/calculate/bazi \
  -H "Content-Type: application/json" \
  -d '{"name": "张三", "gender": "male", "birth_datetime": "1990-05-15 15:00"}'
```

### 方式 3：Python 代码

```python
import xuanxue.core.methods  # 自动注册所有方法
from xuanxue.core.registry import registry, MethodStatus, MethodResult
from xuanxue.core.dispatcher import resolve_methods
from xuanxue.core.synthesis import SynthesisEngine
from xuanxue.analyzers.dimension_extractor import extract_dimensions
from xuanxue.export.report import build_report, to_markdown

# 准备输入数据
input_data = {
    "name": "张三",
    "gender": "male",
    "birth_datetime": "1990-05-15 15:00",
}

# 运行所有方法
results = resolve_methods("综合分析", registry, input_data)

# 提取维度信号
enriched = []
for r in results:
    if r.status == MethodStatus.RUNNABLE and r.facts:
        dims = extract_dimensions(r.method, r.facts)
        enriched.append(MethodResult(
            method=r.method, status=r.status,
            facts={**r.facts, **dims},
        ))

# 交叉验证
synthesis = SynthesisEngine().synthesize(enriched)

# 生成报告
method_results = {r.method: r.facts for r in results if r.status == MethodStatus.RUNNABLE}
report = build_report("张三", input_data, method_results, {
    "final_verdict": synthesis.final_verdict,
    "runnable_methods": synthesis.runnable_methods,
    "blocked_methods": synthesis.blocked_methods,
    "dimension_verdicts": [
        {"dimension": v.dimension, "best_method": v.best_method,
         "confidence": v.confidence, "consensus": v.consensus}
        for v in synthesis.dimensions
    ],
})
print(to_markdown(report))
```

### 方式 4：Claude Code Skill

在 Claude Code 中直接说以下关键词即可触发：

- "我想算命"
- "帮我看看八字"
- "紫微斗数分析"
- "综合命理分析"
- "算一卦"
- "看运势"

---

## 📁 项目结构

```
xuanxue-ai/
├── SKILL.md                      # Claude Code Skill 入口
├── Dockerfile                    # Docker 部署配置
├── pyproject.toml                # 项目配置和依赖
├── README.md                     # 中文说明文档
├── README_EN.md                  # 英文说明文档
├── src/xuanxue/
│   ├── core/                     # 核心模块
│   │   ├── input_schema.py       # 统一输入 Schema（Pydantic）
│   │   ├── registry.py           # 技法注册表 + 状态机
│   │   ├── dispatcher.py         # 自然语言路由
│   │   ├── synthesis.py          # 加权交叉验证引擎
│   │   ├── methods.py            # 方法自动注册
│   │   ├── cli.py                # CLI 命令行入口
│   │   └── calendar_utils.py     # 农历→公历转换
│   ├── calculators/              # 确定性计算引擎（11个）
│   │   ├── bazi_engine.py        # 八字排盘
│   │   ├── ziwei_engine.py       # 紫微斗数
│   │   ├── qimen_engine.py       # 奇门遁甲
│   │   ├── chenggu_engine.py     # 称骨算命
│   │   ├── numerology_engine.py  # 数字命理
│   │   ├── meihua_engine.py      # 梅花易数
│   │   ├── liuyao_engine.py      # 六爻排盘
│   │   ├── liuren_engine.py      # 大六壬
│   │   ├── jinkou_engine.py      # 金口诀
│   │   ├── western_engine.py     # 西方占星
│   │   └── vedic_engine.py       # 吠陀占星
│   ├── analyzers/
│   │   ├── prompts.py            # LLM 分析约束 Prompt
│   │   └── dimension_extractor.py # 维度信号提取
│   ├── export/
│   │   └── report.py             # 报告导出（MD/JSON/Text）
│   └── server.py                 # FastAPI HTTP 服务
├── tests/                        # 86 个测试
│   ├── test_bazi_engine.py
│   ├── test_input_schema.py
│   ├── test_new_engines.py
│   ├── test_new_calculators.py
│   └── test_report.py
└── references/                   # 参考资料（预留）
```

---

## 🎯 设计理念

### 反幻觉设计

```
用户输入 → Python 计算引擎（确定性） → 结构化数据 → LLM 解读（受约束）
```

- **排盘计算**：由 Python 引擎完成，结果精确可复现
- **LLM 解读**：只基于计算结果做解读，引用经典典籍
- **六维度验证**：多法交叉验证，避免单一方法偏差

### 六维度归一化

| 维度 | 分析内容 | 重要性 |
|------|---------|--------|
| **性格** | 底层气质、行为模式、优缺点 | ★★★★★ |
| **事业** | 适配场景、发展方向、行业建议 | ★★★★★ |
| **财运** | 资源模式、理财建议、求财方向 | ★★★★ |
| **关系** | 亲密模式、人际特点、婚姻建议 | ★★★★ |
| **身心** | 压力来源、健康注意、养生建议 | ★★★ |
| **阶段** | 运势节奏、关键年份、把握时机 | ★★★★★ |

---

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试文件
python -m pytest tests/test_bazi_engine.py -v

# 查看测试覆盖率
python -m pytest tests/ --cov=xuanxue

# 查看测试数量
python -m pytest tests/ --co -q
```

### 测试覆盖

| 测试文件 | 测试数量 | 覆盖内容 |
|---------|---------|---------|
| test_bazi_engine.py | 11 | 八字排盘、十神、藏干、大运 |
| test_input_schema.py | 10 | 输入验证、Schema |
| test_new_engines.py | 17 | 紫微、奇门、称骨、注册表 |
| test_new_calculators.py | 18 | 7个新计算器 |
| test_report.py | 17 | 报告导出、HTTP API |
| **总计** | **86** | **全部通过** |

---

## 🐳 Docker 部署

### 构建和运行

```bash
# 构建镜像
docker build -t xuanxue-ai .

# 运行容器
docker run -d -p 8600:8600 --name xuanxue xuanxue-ai

# 查看日志
docker logs xuanxue

# 停止容器
docker stop xuanxue
```

### 验证部署

```bash
# 健康检查
curl http://localhost:8600/health

# 分析请求
curl -X POST http://localhost:8600/analyze \
  -H "Content-Type: application/json" \
  -d '{"name":"测试","gender":"male","birth_datetime":"1990-05-15 15:00"}'
```

---

## ❓ 常见问题

### Q: 安装时提示 "Python version not supported"？

A: 本项目需要 Python 3.11 或更高版本。请检查版本：
```bash
python --version
```

### Q: 运行时报错 "No module named xuanxue"？

A: 请确保已激活虚拟环境并安装了项目：
```bash
source .venv/bin/activate
pip install -e .
```

### Q: 如何修改服务端口？

A: 编辑 `src/xuanxue/server.py` 中的 `port` 变量。

### Q: 农历日期如何输入？

A: 在 `birth_datetime` 字段使用公历日期。如需农历转换：
```python
from xuanxue.core.calendar_utils import lunar_to_solar
solar_date = lunar_to_solar(1987, 8, 18)  # 农历1987年8月18日
print(solar_date)  # 1987-10-10
```

---

## 📚 经典引用

本项目参考了以下经典著作：

- 《穷通宝典》— 调候用神
- 《三命通会》— 论用神
- 《滴天髓》— 天道抑扶
- 《渊海子平》— 八字基础
- 《子平真诠》— 格局理论
- 《紫微斗数全书》— 紫微排盘
- 《烟波钓叟歌》— 奇门遁甲

---

## ⚠️ 免责声明

命理分析仅供文化研究和参考，不应被视为科学预测。人生在于自身的努力和选择。

---

## 📄 License

MIT License

---

## 🙏 致谢

感谢以下开源项目的灵感：

- [bazi-skill](https://github.com/jinchenma94/bazi-skill) — 八字分析框架
- [Numerologist_skills](https://github.com/FANzR-arch/Numerologist_skills) — 反幻觉设计理念
- [yuan](https://github.com/shizhilya/yuan) — 统一输入 Schema
