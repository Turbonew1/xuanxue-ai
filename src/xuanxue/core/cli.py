"""命令行入口"""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="综合玄学命理分析")
    sub = parser.add_subparsers(dest="command")

    p_analyze = sub.add_parser("analyze", help="综合命理分析")
    p_analyze.add_argument("--name", default="命主", help="姓名")
    p_analyze.add_argument("--gender", required=True, choices=["male", "female"])
    p_analyze.add_argument("--birth", required=True, help="出生时间 YYYY-MM-DD HH:MM")
    p_analyze.add_argument("--place", default="", help="出生地")
    p_analyze.add_argument("--methods", nargs="*", help="指定方法（留空=全部）")
    p_analyze.add_argument("--format", choices=["json", "markdown", "text"], default="markdown")

    sub.add_parser("serve", help="启动 HTTP 服务")
    sub.add_parser("methods", help="列出所有方法")

    args = parser.parse_args()

    if args.command == "methods":
        _show_methods()
    elif args.command == "analyze":
        _run_analyze(args)
    elif args.command == "serve":
        _run_server()
    else:
        parser.print_help()


def _show_methods() -> None:
    from xuanxue.core.registry import registry
    import xuanxue.core.methods  # noqa: F401
    for entry in registry.list_all():
        print(f"  {entry.name:12s} {entry.display_name:10s} {entry.description}")


def _run_analyze(args: argparse.Namespace) -> None:
    import xuanxue.core.methods  # noqa: F401
    from xuanxue.core.dispatcher import resolve_methods, select_for_full_reading
    from xuanxue.core.registry import MethodStatus, MethodResult
    from xuanxue.core.synthesis import SynthesisEngine
    from xuanxue.analyzers.dimension_extractor import extract_dimensions
    from xuanxue.export.report import build_report, to_markdown, to_json, to_text
    from xuanxue.core.registry import registry

    input_data = {
        "name": args.name,
        "gender": args.gender,
        "birth_datetime": args.birth,
        "birthplace": args.place,
    }

    results = resolve_methods("综合分析", registry, input_data)
    selected_names = select_for_full_reading(registry, input_data)
    selected = [r for r in results if r.method in selected_names]

    # 提取维度信号并注入
    enriched: list[MethodResult] = []
    for r in selected:
        if r.status == MethodStatus.RUNNABLE and r.facts:
            dims = extract_dimensions(r.method, r.facts)
            enriched_facts = {**r.facts, **dims}
            enriched.append(MethodResult(
                method=r.method, status=r.status, facts=enriched_facts,
                interpretation=r.interpretation, confidence=r.confidence,
                blockers=r.blockers, evidence=r.evidence,
            ))
        else:
            enriched.append(r)

    engine = SynthesisEngine()
    synthesis = engine.synthesize(enriched)

    method_results = {}
    for r in results:
        if r.status == MethodStatus.RUNNABLE and r.facts:
            method_results[r.method] = r.facts

    synthesis_dict = {
        "final_verdict": synthesis.final_verdict,
        "runnable_methods": synthesis.runnable_methods,
        "blocked_methods": synthesis.blocked_methods,
        "dimension_verdicts": [
            {"dimension": v.dimension, "best_method": v.best_method,
             "confidence": v.confidence, "consensus": v.consensus}
            for v in synthesis.dimensions
        ],
    }
    report = build_report(args.name, input_data, method_results, synthesis_dict)

    formatter = {"json": to_json, "markdown": to_markdown, "text": to_text}[args.format]
    print(formatter(report))


def _run_server() -> None:
    from xuanxue.server import main as server_main
    server_main()


if __name__ == "__main__":
    main()
