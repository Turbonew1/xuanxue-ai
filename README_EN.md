# 🔮 Xuanxue AI — Chinese Metaphysics Analysis Engine

> Comprehensive fortune-telling analysis skill — A unified engine combining **11 metaphysics methods**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-86%20passing-brightgreen.svg)](#testing)

[中文](README.md) | English

---

## ✨ Features

- **11 Metaphysics Methods**: BaZi, Zi Wei Dou Shu, Qi Men Dun Jia, Cheng Gu, Numerology, Mei Hua, Liu Yao, Liu Ren, Jin Kou Jue, Western Astrology, Vedic Astrology
- **Deterministic Calculation**: Chart engines implemented in Python, results are precise and reproducible
- **6-Dimension Cross-Validation**: Personality/Career/Wealth/Relationship/Health/Timing
- **Anti-Hallucination Design**: LLM only interprets and advises, never calculates charts
- **Detailed Reports**: Includes remedies, yearly predictions, and lucky configurations

---

## 🚀 Quick Start

### Option 1: pip install (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/Turbonew1/xuanxue-ai.git
cd xuanxue-ai

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or .venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -e .

# 4. Verify installation
python -m xuanxue.core.cli methods
```

### Option 2: uv install (Faster)

```bash
# 1. Install uv (if not installed)
pip install uv

# 2. Clone the repository
git clone https://github.com/Turbonew1/xuanxue-ai.git
cd xuanxue-ai

# 3. Create virtual environment and install
uv venv .venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# 4. Verify installation
python -m xuanxue.core.cli methods
```

### Option 3: Docker

```bash
# 1. Clone the repository
git clone https://github.com/Turbonew1/xuanxue-ai.git
cd xuanxue-ai

# 2. Build image
docker build -t xuanxue-ai .

# 3. Run container
docker run -p 8600:8600 xuanxue-ai

# 4. Verify (in new terminal)
curl http://localhost:8600/health
```

### Verify Installation

```bash
# List all supported methods
python -m xuanxue.core.cli methods

# Output example:
#   bazi         BaZi           Four Pillars charting and analysis
#   ziwei        Zi Wei Dou Shu Purple Star Astrology charting
#   qimen        Qi Men Dun Jia Qi Men Dun Jia charting
#   chenggu      Cheng Gu       Bone Weight fortune telling
#   numerology   Numerology     Five Grid analysis and Life Number
#   meihua       Mei Hua        Plum Blossom numerology
#   liuyao       Liu Yao        Six Lines divination
#   liuren       Liu Ren        Six Ren divination
#   jinkou       Jin Kou Jue    Golden Mouth Formula
#   western      Western Astro  Sun/Moon/Rising sign analysis
#   vedic        Vedic Astro    Sidereal astrology and Nakshatra
```

---

## 📊 Supported Methods (11 Total)

| Method | Engine | Function | Required Info |
|--------|--------|----------|---------------|
| **BaZi** | `bazi_engine` | Four Pillars, Ten Gods, Hidden Stems, Five Elements, Luck Pillars | Birth time, Gender |
| **Zi Wei** | `ziwei_engine` | 12 Palaces, Main Stars, Four Transformations, Decades | Birth time, Gender |
| **Qi Men** | `qimen_engine` | 9 Palaces, 8 Gates, 9 Stars, 8 Gods | Birth time |
| **Cheng Gu** | `chenggu_engine` | Bone Weight calculation, Verse interpretation | Birth time |
| **Numerology** | `numerology_engine` | Five Grid analysis, Life Number | Name, Birth time |
| **Mei Hua** | `meihua_engine` | Time-based hexagram, Body-Use relationship | Birth time |
| **Liu Yao** | `liuyao_engine` | Six Lines, World/Response positions, Six Spirits | Birth time |
| **Liu Ren** | `liuren_engine` | Month General + Hour, Four Lessons | Birth time |
| **Jin Kou** | `jinkou_engine` | Four Pillars lesson, Five Element analysis | Birth time |
| **Western** | `western_engine` | Sun/Moon/Rising signs, Four Elements | Birth time |
| **Vedic** | `vedic_engine` | Sidereal zodiac, Nakshatra, Tithi | Birth time |

---

## 🎯 Usage

### Option 1: CLI Command Line

```bash
# Comprehensive analysis (auto-selects all methods)
python -m xuanxue.core.cli analyze \
  --name "John" \
  --gender male \
  --birth "1990-05-15 15:00" \
  --format markdown

# Specify methods
python -m xuanxue.core.cli analyze \
  --name "Jane" \
  --gender female \
  --birth "1988-12-25 08:30" \
  --methods bazi ziwei chenggu \
  --format json

# Output as JSON
python -m xuanxue.core.cli analyze \
  --name "Mike" \
  --gender male \
  --birth "1985-03-20 10:30" \
  --format json
```

### Option 2: HTTP API

```bash
# Start server
python -m xuanxue.server

# In another terminal:
# Health check
curl http://localhost:8600/health

# List all methods
curl http://localhost:8600/methods

# Comprehensive analysis
curl -X POST http://localhost:8600/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John",
    "gender": "male",
    "birth_datetime": "1990-05-15 15:00",
    "birthplace": "Beijing"
  }'

# Single method calculation
curl -X POST http://localhost:8600/calculate/bazi \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "gender": "male", "birth_datetime": "1990-05-15 15:00"}'
```

### Option 3: Python Code

```python
import xuanxue.core.methods  # Auto-registers all methods
from xuanxue.core.registry import registry, MethodStatus, MethodResult
from xuanxue.core.dispatcher import resolve_methods
from xuanxue.core.synthesis import SynthesisEngine
from xuanxue.analyzers.dimension_extractor import extract_dimensions
from xuanxue.export.report import build_report, to_markdown

# Prepare input data
input_data = {
    "name": "John",
    "gender": "male",
    "birth_datetime": "1990-05-15 15:00",
}

# Run all methods
results = resolve_methods("comprehensive analysis", registry, input_data)

# Extract dimension signals
enriched = []
for r in results:
    if r.status == MethodStatus.RUNNABLE and r.facts:
        dims = extract_dimensions(r.method, r.facts)
        enriched.append(MethodResult(
            method=r.method, status=r.status,
            facts={**r.facts, **dims},
        ))

# Cross-validation
synthesis = SynthesisEngine().synthesize(enriched)

# Generate report
method_results = {r.method: r.facts for r in results if r.status == MethodStatus.RUNNABLE}
report = build_report("John", input_data, method_results, {
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

### Option 4: Claude Code Skill

In Claude Code, simply say these keywords to trigger:

- "I want to have my fortune told"
- "Help me read my BaZi"
- "Zi Wei Dou Shu analysis"
- "Comprehensive fortune analysis"
- "Read my hexagram"
- "Check my fortune"

---

## 📁 Project Structure

```
xuanxue-ai/
├── SKILL.md                      # Claude Code Skill entry
├── Dockerfile                    # Docker deployment
├── pyproject.toml                # Project config & dependencies
├── README.md                     # Chinese documentation
├── README_EN.md                  # English documentation
├── src/xuanxue/
│   ├── core/                     # Core modules
│   │   ├── input_schema.py       # Unified input schema (Pydantic)
│   │   ├── registry.py           # Method registry + state machine
│   │   ├── dispatcher.py         # Natural language routing
│   │   ├── synthesis.py          # Weighted cross-validation engine
│   │   ├── methods.py            # Auto method registration
│   │   ├── cli.py                # CLI entry point
│   │   └── calendar_utils.py     # Lunar → Solar conversion
│   ├── calculators/              # Deterministic chart engines (11)
│   │   ├── bazi_engine.py        # BaZi charting
│   │   ├── ziwei_engine.py       # Zi Wei Dou Shu
│   │   ├── qimen_engine.py       # Qi Men Dun Jia
│   │   ├── chenggu_engine.py     # Cheng Gu (Bone Weight)
│   │   ├── numerology_engine.py  # Numerology (Five Grid)
│   │   ├── meihua_engine.py      # Mei Hua (Plum Blossom)
│   │   ├── liuyao_engine.py      # Liu Yao (Six Lines)
│   │   ├── liuren_engine.py      # Liu Ren (Six Ren)
│   │   ├── jinkou_engine.py      # Jin Kou Jue
│   │   ├── western_engine.py     # Western Astrology
│   │   └── vedic_engine.py       # Vedic Astrology
│   ├── analyzers/
│   │   ├── prompts.py            # LLM analysis constraint prompts
│   │   └── dimension_extractor.py # Dimension signal extraction
│   ├── export/
│   │   └── report.py             # Report export (MD/JSON/Text)
│   └── server.py                 # FastAPI HTTP server
├── tests/                        # 86 tests
│   ├── test_bazi_engine.py
│   ├── test_input_schema.py
│   ├── test_new_engines.py
│   ├── test_new_calculators.py
│   └── test_report.py
└── references/                   # Reference materials (reserved)
```

---

## 🎯 Design Philosophy

### Anti-Hallucination Design

```
User Input → Python Chart Engine (Deterministic) → Structured Data → LLM Interpretation (Constrained)
```

- **Chart Calculation**: Done by Python engines, results are precise and reproducible
- **LLM Interpretation**: Only interprets based on calculation results, citing classical texts
- **6-Dimension Verification**: Multi-method cross-validation to avoid single-method bias

### 6-Dimension Normalization

| Dimension | Analysis Content | Importance |
|-----------|-----------------|------------|
| **Personality** | Core temperament, behavior patterns, strengths/weaknesses | ★★★★★ |
| **Career** | Suitable scenarios, development direction, industry advice | ★★★★★ |
| **Wealth** | Resource patterns, financial advice, wealth direction | ★★★★ |
| **Relationship** | Intimate patterns, interpersonal traits, marriage advice | ★★★★ |
| **Health** | Stress sources, health concerns, wellness advice | ★★★ |
| **Timing** | Fortune rhythm, key years, seizing opportunities | ★★★★★ |

### Method Weights

| Method | Weight | Description |
|--------|--------|-------------|
| BaZi | ★★★★★ | Core method, highest weight |
| Zi Wei | ★★★★★ | Core method, highest weight |
| Qi Men | ★★★★ | Important reference |
| Mei Hua | ★★★★ | Important reference |
| Liu Yao | ★★★★ | Important reference |
| Liu Ren | ★★★★ | Important reference |
| Cheng Gu | ★★★ | Supplementary reference |
| Numerology | ★★★ | Supplementary reference |
| Jin Kou | ★★★ | Supplementary reference |
| Western | ★★★ | Supplementary reference |
| Vedic | ★★★ | Supplementary reference |

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_bazi_engine.py -v

# View test coverage
python -m pytest tests/ --cov=xuanxue

# Count tests
python -m pytest tests/ --co -q
```

### Test Coverage

| Test File | Tests | Coverage |
|-----------|-------|----------|
| test_bazi_engine.py | 11 | BaZi charting, Ten Gods, Hidden Stems, Luck Pillars |
| test_input_schema.py | 10 | Input validation, Schema |
| test_new_engines.py | 17 | Zi Wei, Qi Men, Cheng Gu, Registry |
| test_new_calculators.py | 18 | 7 new calculators |
| test_report.py | 17 | Report export, HTTP API |
| **Total** | **86** | **All passing** |

---

## 🐳 Docker Deployment

### Build and Run

```bash
# Build image
docker build -t xuanxue-ai .

# Run container
docker run -d -p 8600:8600 --name xuanxue xuanxue-ai

# View logs
docker logs xuanxue

# Stop container
docker stop xuanxue
```

### Verify Deployment

```bash
# Health check
curl http://localhost:8600/health

# Analysis request
curl -X POST http://localhost:8600/analyze \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","gender":"male","birth_datetime":"1990-05-15 15:00"}'
```

---

## ❓ FAQ

### Q: Installation error "Python version not supported"?

A: This project requires Python 3.11 or higher. Check your version:
```bash
python --version
```

### Q: Error "No module named xuanxue"?

A: Make sure you've activated the virtual environment and installed the project:
```bash
source .venv/bin/activate
pip install -e .
```

### Q: How to change the server port?

A: Edit the `port` variable in `src/xuanxue/server.py`.

### Q: How to input lunar calendar dates?

A: Use solar dates in the `birth_datetime` field. For lunar conversion:
```python
from xuanxue.core.calendar_utils import lunar_to_solar
solar_date = lunar_to_solar(1987, 8, 18)  # Lunar Aug 18, 1987
print(solar_date)  # 1987-10-10
```

### Q: How to add a new metaphysics method?

A: Follow these steps:
1. Create a new engine file in `calculators/` directory
2. Implement `calculate_xxx(input_data)` function
3. Register in `core/methods.py`
4. Add weights in `core/synthesis.py`
5. Add dimension extraction in `analyzers/dimension_extractor.py`

---

## 📚 Classical References

This project references the following classical texts:

- *Qiong Tong Bao Dian* (穷通宝典) — Seasonal adjustments
- *San Ming Tong Hui* (三命通会) — On Useful Gods
- *Di Tian Sui* (滴天髓) — Heavenly Dao of Balance
- *Yuan Hai Zi Ping* (渊海子平) — BaZi fundamentals
- *Zi Ping Zhen Quan* (子平真诠) — Pattern theory
- *Zi Wei Dou Shu Quan Shu* (紫微斗数全书) — Zi Wei charting
- *Yan Bo Diao Sou Ge* (烟波钓叟歌) — Qi Men Dun Jia

---

## ⚠️ Disclaimer

Fortune analysis is for cultural research and reference only, and should not be regarded as scientific prediction. Life depends on one's own efforts and choices.

---

## 📄 License

MIT License

---

## 🙏 Acknowledgments

Thanks to these open-source projects for inspiration:

- [bazi-skill](https://github.com/jinchenma94/bazi-skill) — BaZi analysis framework
- [Numerologist_skills](https://github.com/FANzR-arch/Numerologist_skills) — Anti-hallucination design
- [yuan](https://github.com/shizhilya/yuan) — Unified input schema
