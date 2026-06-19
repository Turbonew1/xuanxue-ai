# xuanxue-unified-skill

综合玄学 Skill — 融合八字、紫微、奇门、称骨、占星等多套方法的统一命理分析引擎。

## 特性

- **统一输入 Schema** — 一个输入包跑所有技法
- **确定性排盘引擎** — 排盘计算由 Python 完成，LLM 只做解读
- **反幻觉设计** — 缺数据就追问，不硬排、不编造
- **六维度归一化输出** — 性格/事业/财运/关系/身心/阶段
- **多技法交叉验证** — 多个方法结果相互印证

## 安装

```bash
cd xuanxue-unified-skill
uv venv .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## 测试

```bash
pytest tests/ -v
```

## 项目结构

```
xuanxue-unified-skill/
├── SKILL.md                    # Claude Code Skill 入口
├── src/xuanxue/
│   ├── core/
│   │   ├── input_schema.py     # 统一输入 Schema
│   │   ├── registry.py         # 技法注册表
│   │   ├── dispatcher.py       # 自然语言路由
│   │   └── synthesis.py        # 多技法交叉验证
│   ├── calculators/
│   │   └── bazi_engine.py      # 八字排盘
│   ├── analyzers/
│   └── export/
├── references/
└── tests/
```

## License

MIT
